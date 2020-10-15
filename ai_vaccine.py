from city import City
from person import Person
from vaccine import VaccineBase
import torch
import copy


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
            # Add 3 hidden layers
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
        same sized tensor indicating whether that person (a) got COVID [1], (b) should be
        ignored [0] or (c) didn't get covid [-1]
        :param prediction: an (N, ) sized tensor
        :param actual: an (N, ) sized tensor
        :return: a number representing the effectiveness of the scoring. Smaller is better.
        """
        return (prediction * actual).sum()


class VaccineAI(VaccineBase):
    def __init__(self, vaccine_name: str):
        super().__init__(vaccine_name)
        self.nn = PredictorNN(input_features=10, hidden_features=20, hidden_layers=3)

    def train(self):
        pass

    def assign_scores(self, city: City):
        pass

    def get_inputs(self) -> torch.Tensor:
        pass

    def get_actual(self) -> torch.Tensor:
        pass

    def get_prediction(self) -> torch.Tensor:
        pass
