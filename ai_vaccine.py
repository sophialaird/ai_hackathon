from city import City
from person import Person
from vaccine import VaccineBase
from settings import *
import typing as t
import time
import torch


class PredictorNN(torch.nn.Module):
    """
    Takes in a dataset (N, C) of N people and C features per person and
    returns a tensor (N, ) of scores between [0, 1] used to determine the covid score
    """
    def __init__(self, input_features: int, hidden_features: int, hidden_layers: int):
        super().__init__()
        self.input_layer = torch.nn.Linear(in_features=input_features, out_features=hidden_features)
        self.hidden_layers = torch.nn.ModuleList()
        self.hidden_layers.append(torch.nn.Tanh())
        for hidden in range(hidden_layers):
            self.hidden_layers.append(torch.nn.Linear(in_features=hidden_features, out_features=hidden_features))
            self.hidden_layers.append(torch.nn.Tanh())
        self.output_layer = torch.nn.Linear(in_features=hidden_features, out_features=1)
        self.output_norm = torch.nn.Sigmoid()

    def forward(self, x: torch.Tensor):
        y_pred = self.input_layer(x)
        for hidden_layer in self.hidden_layers:
            y_pred = hidden_layer(y_pred)
        y_pred = self.output_layer(y_pred)
        y_pred = self.output_norm(y_pred)
        return y_pred


class COVIDloss(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, prediction: torch.Tensor, actual: torch.Tensor) -> torch.Tensor:
        """
        Prediction is the tensor representing the covid score. Actual is another
        same sized tensor indicating whether that person (a) got COVID [1 or 2], (b) should be
        ignored [0] or (c) didn't get covid [-1]
        :param prediction: an (N, ) sized tensor
        :param actual: an (N, ) sized tensor
        :return: a number representing the effectiveness of the scoring. Smaller is better.
        """
        return (prediction * actual).mean()


class VaccineAI(VaccineBase):
    INPUT_FEATURES = 6
    HIDDEN_FEATURES = INPUT_FEATURES*3
    HIDDEN_LAYERS = 3
    TRAINING_CITY_SIZE = 1000
    TRAINING_INITIAL_SICK = 100
    TRAINING_DAYS = 180

    def __init__(self, vaccine_name: str):
        super().__init__(vaccine_name)
        self.nn = PredictorNN(
            input_features=self.INPUT_FEATURES,
            hidden_features=self.HIDDEN_FEATURES,
            hidden_layers=self.HIDDEN_LAYERS
        )

    def train(self, max_cycles: int = 100):
        print(f"Training {self.name} for {max_cycles} cycles")
        self.nn.train()
        optimizer = torch.optim.Adam(self.nn.parameters(), lr=0.01)
        loss_fn = COVIDloss()
        train_start_time = time.perf_counter()
        for cycle in range(max_cycles):
            start_time = time.perf_counter()

            # Make a random city
            city = City(name='test', size=self.TRAINING_CITY_SIZE, initial_sick=self.TRAINING_INITIAL_SICK)
            self.assign_scores(city)
            for _ in range(self.TRAINING_DAYS):
                city.run_timestep()

            # Training cycle
            x = self.get_inputs(city)
            actual = self.get_actual(city)
            optimizer.zero_grad()
            pred = self.nn(x)
            loss = loss_fn(pred, actual)
            loss.backward()
            optimizer.step()

            cycle_time = time.perf_counter() - start_time
            average_time = (time.perf_counter() - train_start_time)/(cycle + 1)
            remaining_time = average_time * (max_cycles - cycle)
            print(
                f"Cycle: {cycle}\t"
                f"loss: {loss.item()}\t"
                f"Time: {cycle_time:0.2f} sec\t"
                f"Remaining: {remaining_time/60:0.1f} min"
            )

    def assign_scores(self, city: City):
        scores: t.List[float] = self.get_prediction(city)
        person: Person
        for idx, person in enumerate(city.pop):
            person.vaccine_score = scores[idx]

    def get_inputs(self, city: City) -> torch.Tensor:
        x: torch.Tensor = torch.zeros(size=(len(city.pop), self.INPUT_FEATURES))
        person: Person
        for idx, person in enumerate(city.pop):
            person_row = torch.as_tensor([
                float(person.age),
                float(person.is_teacher),
                float(person.is_frontline_worker),
                float(person.is_hospital_worker),
                float(person.preexisting_condition),
                float(len(person.shopping)),
            ])
            x[idx] = person_row
        return x

    def get_actual(self, city: City) -> torch.Tensor:
        x: torch.Tensor = torch.zeros(size=(len(city.pop),))
        person: Person
        for idx, person in enumerate(city.pop):
            if person.initially_sick:
                val = 0   # Ignore these people
            elif person.is_alive is False:
                val = 2   # Extra penalty for death
            elif person.was_sick:
                val = 1   # Penalty for getting sick
            else:
                val = -1  # Benefit for not getting sick
            x[idx] = val
        return x

    def get_prediction(self, city: City) -> t.List[float]:
        old_mode = self.nn.training
        x: torch.Tensor = self.get_inputs(city)
        with torch.no_grad():
            self.nn.eval()
            pred = self.nn(x).view(-1).tolist()
        self.nn.train(mode=old_mode)
        return pred

    def save_nn(self):
        model_path = output_dir / f"{self.name}.dat"
        torch.save(self.nn.state_dict(), model_path)

    def load_nn(self):
        model_path = output_dir / f"{self.name}.dat"
        self.nn.load_state_dict(torch.load(model_path))
