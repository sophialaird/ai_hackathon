import dataclasses
from datetime import date
import typing as t
import random


RECOVERY_RATE_STAGE_0 = 0.5   # TODO: need to verify these
RECOVERY_RATE_STAGE_1 = 0.3
RECOVERY_RATE_STAGE_2 = 0.5
RECOVERY_RATE_STAGE_3 = 0.8


@dataclasses.dataclass
class Person:
    # demographics
    household: int
    work: int
    shopping: t.Set[int]
    age: int
    sex_female: bool                                         # True for female, False for male

    # medical info
    vaccine_score: float = -1.0                               # -1 = no vaccine, otherwise [0, 1]
    is_vaccinated: bool = False                               # True if vaccinated, False otherwise
    preexisting_condition: bool = False
    covid_immunity: float = 0                                 # 0 = vulnerable, 1 = immune
    covid_start_date: t.Optional[date] = None                 # date they first get covid
    covid_end_date: t.Optional[date] = None                   # date they recovered (or the date they died)
    vaccine_date: t.Optional[date] = None                     # date they got the covid vaccine
    visible_symptoms: bool = False                            # has visible symptoms
    sickness_level: int = 0                                   # 0 = no symptoms, 1 = mild, 2 = medium, 3 = high
    is_alive: bool = True
    in_quarantine: bool = False

    @property
    def is_infected(self) -> bool:
        return self.covid_start_date is not None and self.is_alive

    @property
    def is_contagious_outside_home(self) -> bool:
        return self.is_infected and not self.in_quarantine

    @property
    def is_currently_sick(self) -> bool:
        return self.is_alive and self.covid_start_date is not None and self.covid_end_date is None

    @property
    def is_vulnerable(self) -> bool:
        return self.is_alive and self.covid_start_date is None

    @property
    def is_recovered(self) -> bool:
        return self.is_alive and self.covid_start_date is not None and self.covid_end_date is not None

    @property
    def workplace_id(self) -> int:
        if self.is_alive is False or self.in_quarantine:
            return -1
        else:
            return self.work

    @property
    def shopping_id(self) -> t.Set:
        if self.is_alive is False or self.in_quarantine:
            return set()
        else:
            return self.shopping

    def infect(self, dt: date):
        if self.covid_start_date is None:
            self.covid_start_date = dt

    def vaccinate(self):
        self.is_vaccinated = True
        self.covid_immunity = 1.0

    def kill(self, dt: date):
        self.is_alive = False
        self.covid_end_date = dt

    def recover(self, dt: date):
        self.is_alive = True
        self.covid_end_date = dt
        self.covid_immunity = 1.0
        self.in_quarantine = False

    def update_health(self, current_date: date):
        if self.covid_end_date is not None:
            return
        if self.covid_start_date is None:
            return
        days_since_infection = (current_date - self.covid_start_date).days
        if days_since_infection == 3:
            self.sickness_level = 0
            self.visible_symptoms = False
        elif days_since_infection == 5:
            self.visible_symptoms = True
        elif days_since_infection == 10:
            if random.random() < RECOVERY_RATE_STAGE_0:
                self.recover(current_date)
                return
            self.sickness_level = 1
            self.in_quarantine = True
        elif days_since_infection == 15:
            if random.random() < RECOVERY_RATE_STAGE_1:
                self.recover(current_date)
                return
            self.sickness_level = 2
        elif days_since_infection == 24:
            if random.random() < RECOVERY_RATE_STAGE_2:
                self.recover(current_date)
                return
            self.sickness_level = 3
        elif days_since_infection == 35:
            if random.random() < RECOVERY_RATE_STAGE_3:
                self.recover(current_date)
                return
            self.kill(current_date)
        else:
            # Nothing happens on these dates
            pass

