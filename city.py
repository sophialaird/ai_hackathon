from person import Person
import typing as t
from datetime import date, timedelta
import random


class City:
    def __init__(self, size: int = 1000):
        self.pop: t.List[Person] = []
        self.start_date: date = date(2021, 1, 1)
        self.current_date: date = self.start_date
        for i in range(size):
            person = Person(
                household=random.randint(0, size//4),
                work=random.randint(0, 20),
                shopping=set([random.randint(0, 20) for r in range(20)]),
                age=10,
                sex_female=True if random.random() >= 0.5 else False,
                is_alive=True
            )
            self.pop.append(person)

    @property
    def starting_population(self) -> int:
        return len(self.pop)

    @property
    def population(self) -> int:
        return sum([p.is_alive for p in self.pop])

    @property
    def sex_distribution(self) -> float:
        """
        Returns the % of the population that is female
        :return: [0, 1]
        """
        return sum([p.sex_female for p in self.pop]) / self.starting_population

    @property
    def cumulative_sick(self) -> int:
        return sum([p.covid_start_date is not None for p in self.pop])

    @property
    def number_dead(self) -> int:
        return sum([p.is_alive is False for p in self.pop])

    @property
    def cumulative_recovered(self) -> int:
        return sum([p.covid_end_date is not None and p.is_alive for p in self.pop])

    @property
    def total_uninfected(self) -> int:
        return sum([p.covid_start_date is None for p in self.pop])

    # --------------------------------------------------------------------------------------------
    def run_timestep(self):
        """
        Timestep to update the population
            Step 1: Go to work - count interactions with infected people
            Step 2: Go home - count interactions with infected people
            Step 3: Go shopping - count interactions with infected people
            Step 4: Update vaccine
            Step 5: Update health

        :return:
        """
        self.step1_work()
        self.step2_home()
        self.step3_shopping()
        self.step4_vaccine()
        self.step5_health()
        self.current_date += timedelta(days=1)

    def step1_work(self):
        pass

    def step2_home(self):
        pass

    def step3_shopping(self):
        pass

    def step4_vaccine(self):
        pass

    def step5_health(self):
        pass