import dataclasses
from datetime import date
import typing as t
import random

from settings import *


@dataclasses.dataclass
class Person:
    # demographics
    household: int
    work: int
    shopping: t.Set[int]
    age: int
    sex_female: bool                                         # True for female, False for male
    preexisting_condition: bool = False

    # medical info
    initially_sick: bool = False                              # True if initially sick (in setup) or False otherwise
    vaccine_score: float = -1.0                               # -1 = no vaccine, otherwise [0, 1]
    is_vaccinated: bool = False                               # True if vaccinated, False otherwise
    vaccine_wasted: bool = False                              # True if given vaccine but already infected
    covid_immunity: float = 0                                 # 0 = vulnerable, 1 = immune
    covid_start_date: t.Optional[date] = None                 # date they first get covid
    covid_end_date: t.Optional[date] = None                   # date they recovered (or the date they died)
    vaccine_date: t.Optional[date] = None                     # date they got the covid vaccine
    visible_symptoms: bool = False                            # has visible symptoms
    sickness_level: int = 0                                   # 0 = no symptoms, 1 = mild, 2 = medium, 3 = high
    is_alive: bool = True
    in_quarantine: bool = False

    # Information ------------------------------------------------------------------------------------------------------
    @property
    def is_teacher(self) -> bool:
        return self.age >= 18 and self.work == SCHOOL_ID

    @property
    def is_hospital_worker(self) -> bool:
        return self.age >= 18 and self.work == HOSPITAL_ID

    @property
    def is_frontline_worker(self) -> bool:
        return self.age >= 18 and self.work == FRONTLINE_ID

    @property
    def was_sick(self) -> bool:
        """
        Was ever sick, currently alive or not
        :return:
        """
        return self.covid_start_date is not None

    @property
    def is_infected(self) -> bool:
        """
        Was ever sick but is still alive
        :return:
        """
        return self.was_sick and self.is_alive

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
        if self.is_alive is False:
            return -1
        elif self.sickness_level == 3:
            return HOSPITAL_ID
        if self.is_alive is False and self.sickness_level >= 1:
            return NO_WORK_ID
        else:
            return self.work

    @property
    def shopping_id(self) -> t.Set:
        if self.is_alive is False or self.in_quarantine:
            return set()
        else:
            return self.shopping

    def chance_of_getting_covid(self, num_interactions: int) -> float:
        """
        Determine the chance of getting COVID after a number of interactions
        :param num_interactions:
        :return:
        """
        probability = (1 + CHANGE_OF_GETTING_SICK_FROM_INTERACTION) ** num_interactions - 1

        # adjust for age
        if self.age >= 70:
            probability *= 2.0
        elif self.age >= 50:
            probability *= 1.5
        elif self.age >= 30:
            probability *= 1.1

        # adjust for pre-existing conditions
        if self.preexisting_condition:
            probability *= 2

        # Adjust for immunity factor
        probability *= (1 - self.covid_immunity)
        return probability

    # Actions ----------------------------------------------------------------------------------------------------------
    def infect(self, dt: date):
        if self.covid_start_date is None:
            self.covid_start_date = dt

    def vaccinate(self):
        self.is_vaccinated = True
        self.covid_immunity = 1.0
        self.vaccine_wasted = self.is_infected   # if vaccinated, but was previously infected, then vaccine is wasted

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

        # Adjust for health factors
        health_factor = 1.5 if self.preexisting_condition else 1.0
        health_factor *= 1.5 if self.age >= 65 else 1.0

        if days_since_infection == 3:
            self.sickness_level = 0
            self.visible_symptoms = False
        elif days_since_infection == 5:
            self.visible_symptoms = True
        elif days_since_infection == 10:
            if random.random() * health_factor < RECOVERY_RATE_STAGE_0:
                self.recover(current_date)
                return
            self.sickness_level = 1
            self.in_quarantine = True
        elif days_since_infection == 15:
            if random.random() * health_factor < RECOVERY_RATE_STAGE_1:
                self.recover(current_date)
                return
            self.sickness_level = 2
        elif days_since_infection == 24:
            if random.random() * health_factor < RECOVERY_RATE_STAGE_2:
                self.recover(current_date)
                return
            self.sickness_level = 3
        elif days_since_infection == 35:
            if random.random() * health_factor < RECOVERY_RATE_STAGE_3:
                self.recover(current_date)
                return
            self.kill(current_date)
        else:
            # Nothing happens on any other dates
            pass
