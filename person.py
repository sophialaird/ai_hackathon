import dataclasses
from datetime import date
import typing as t


@dataclasses.dataclass
class Person:
    # demographics
    household: int
    work: int
    shopping: t.Set[int]
    age: int
    sex_female: bool                                         # True for female, False for male

    # medical info
    preexisting_condition: bool = False
    covid_immunity: float = 0                                 # 0 = vulnerable, 1 = immune
    covid_start_date: t.Optional[date] = None                 # date they first get covid
    covid_end_date: t.Optional[date] = None                   # date they recovered (or the date they died)
    vaccine_date: t.Optional[date] = None                     # date they got the covid vaccine
    visible_symptoms: bool = False                            # has visible symptoms
    sickness_level: int = 0                                   # 0 = no symptoms, 1 = mild, 2 = medium, 3 = high
    is_alive: bool = True

    def infect(self, dt: date):
        self.covid_start_date = dt

    def kill(self, dt: date):
        self.is_alive = False
        self.covid_end_date = dt

    def recover(self, dt: date):
        self.covid_end_date = dt
        self.covid_immunity = 1.0
