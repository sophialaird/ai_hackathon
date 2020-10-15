from person import Person
import typing as t
from datetime import date, timedelta
from settings import *
import random


class City:
    def __init__(self, name: str, size: int = 1000, initial_sick: int = 100):
        self.name = name
        self.pop: t.List[Person] = []                        # holds a list of people
        self.households: t.Dict[int, t.Set[int]] = dict()    # gives the set of people in a household
        self.work: t.Dict[int, t.Set[int]] = dict()          # gives the set of people at a workplace
        self.shopping: t.Dict[int, t.Set[int]] = dict()      # gives the set of people at a shopping place
        self.start_date: date = date(2021, 1, 1)
        self.current_date: date = self.start_date
        self.vaccine_dates: t.List[date] = [self.start_date + timedelta(days=15 * (i + 1)) for i in range(10)]
        self.vaccine_order: t.List[int] = []                 # a list showing the order people get their vaccines
        self.add_people(pop_size=size)
        self.create_sick_people(initial_sick)
        self.build_helpers()

    @property
    def starting_population(self) -> int:
        return len(self.pop)

    @property
    def population(self) -> int:
        return sum([p.is_alive for p in self.pop])

    @property
    def female_pct(self) -> float:
        """
        Returns the % of the population that is female
        :return: [0, 1]
        """
        return sum([p.sex_female for p in self.pop]) / self.starting_population

    @property
    def num_dead(self) -> int:
        """
        Finds the number of people who have died at the current date
        :return:
        """
        return sum([not p.is_alive for p in self.pop])

    @property
    def num_sick(self) -> int:
        """
        Finds the number of people who are sick at the current date
        :return:
        """
        return sum([p.is_currently_sick for p in self.pop])

    @property
    def num_recovered(self) -> int:
        """
        Finds the number of people who have recovered from covid at the current date
        :return:
        """
        return sum([p.is_recovered for p in self.pop])

    @property
    def num_uninfected(self) -> int:
        """
        Finds the number of people who are uninfected from covid at the current date
        :return:
        """
        return sum([p.is_vulnerable for p in self.pop])

    @property
    def num_vaccinated(self) -> int:
        """
        Finds the number of people who have been vaccinated
        :return:
        """
        return sum([p.is_vaccinated for p in self.pop])

    @property
    def num_wasted_vaccines(self) -> int:
        """
        Finds the number of people who were vaccinated but already sick
        :return:
        """
        return sum([p.vaccine_wasted for p in self.pop])

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
        interactions = [0] * len(self.pop)
        sick_people = self.get_sick_people()
        self.step1_work(interactions, sick_people)
        self.step2_home(interactions, sick_people)
        self.step3_shopping(interactions, sick_people)
        self.step4_vaccine()
        self.step5_health_update(interactions)
        self.current_date += timedelta(days=1)
        return self.current_date

    def get_sick_people(self) -> t.List[int]:
        """
        Return the index of all the people who are contagious
        :return:
        """
        return [idx for idx, p in enumerate(self.pop) if p.is_infected]

    def step1_work(self, interactions: t.List[int], sick_people: t.List[int]):
        """
        Update all the interactions a sick person has with everyone else
        :param interactions: a list (size: pop) of all the interactions with sick people from the city
        :param sick_people: a list of all the sick people
        :return:
        """
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            if not sick_person.in_quarantine:
                continue  # Can't get people sick at work if you are in quarantine
            for other_idx in self.work.get(sick_person.work, set()):
                work_person = self.pop[other_idx]
                if work_person.is_vulnerable:
                    interactions[other_idx] += 10

    def step2_home(self, interactions: t.List[int], sick_people: t.List[int]):
        """
        Update all the interactions at home
        :param interactions: a list (size: pop) of all the interactions with sick people from the city
        :param sick_people: a list of all the sick people
        :return:
        """
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            for other_idx in self.households[sick_person.household]:
                home_person = self.pop[other_idx]
                if home_person.is_vulnerable:
                    interactions[other_idx] += 40

    def step3_shopping(self, interactions: t.List[int], sick_people: t.List[int]):
        """
        Update all the interactions from shopping
        :param interactions: a list (size: pop) of all the interactions with sick people from the city
        :param sick_people: a list of all the sick people
        :return:
        """
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            sick_person_places = sick_person.shopping | {sick_person.workplace_id}
            for sick_place in sick_person_places:
                for other_idx in self.shopping.get(sick_place, set()):
                    shop_person = self.pop[other_idx]
                    if shop_person.is_vulnerable:
                        interactions[other_idx] += 5

    def step4_vaccine(self):
        """
        Apply the vaccine, based on the score
        :return:
        """
        if self.current_date not in self.vaccine_dates:
            return
        if len(self.vaccine_order) == 0:
            # make sure we've set up the vaccine order first
            self.set_vaccine_order()
        vaccines_available = len(self.pop) // len(self.vaccine_dates)
        vaccines_given = 0
        for idx in self.vaccine_order:
            person = self.pop[idx]
            if person.is_alive and person.is_vaccinated is False and person.vaccine_score >= 0:
                person.vaccinate()
                vaccines_given += 1
            if vaccines_given >= vaccines_available:
                break

    def step5_health_update(self, interactions: t.List[int]):
        """
        Update everyone's health

        TODO: Modify the chance of sickness by demographic details like age, income level, work from home etc.

        :param interactions: a list (size: pop) of all the interactions with sick people from the city
        :return:
        """
        for idx, person in enumerate(self.pop):
            if person.is_vulnerable:
                num_interactions = interactions[idx]
                chance_of_sickness = (1 + CHANGE_OF_GETTING_SICK_FROM_INTERACTION) ** num_interactions - 1
                chance_of_sickness *= (1 - person.covid_immunity)
                if random.random() < chance_of_sickness:
                    person.infect(self.current_date)

            # update their health
            person.update_health(self.current_date)

    # City Setup -------------------------------------------------------------------------------------------------------
    def add_people(self, pop_size: int):
        """
        Create the people in the city
        :param pop_size:
        :return:
        """
        for i in range(pop_size):
            person = Person(
                household=random.randint(0, pop_size // 4),
                work=random.randint(0, 20),
                shopping=set([random.randint(0, 20) for _ in range(5)]),
                age=10,
                sex_female=True if random.random() >= 0.5 else False,
                is_alive=True
            )
            self.pop.append(person)

    def create_sick_people(self, number_sick: int):
        """
        Create a bunch of random sick people

        :param number_sick:
        :return:
        """
        for sick_idx in random.sample(range(len(self.pop)), number_sick):
            person = self.pop[sick_idx]
            days_since_infection = random.randint(0, 14)
            sick_day = self.start_date - timedelta(days=days_since_infection)
            person.infect(sick_day)
            person.initially_sick = True
            for j in range(days_since_infection):
                person.update_health(sick_day + timedelta(days=j))

    def build_helpers(self):
        """
        Make helpers to easily find people in a household, shopping or workplace
        :return:
        """
        self.households = {
            household_num: set([idx for idx in range(len(self.pop)) if self.pop[idx].household == household_num])
            for household_num in set([p.household for p in self.pop])
        }
        self.work = {
            work_num: set([idx for idx in range(len(self.pop)) if self.pop[idx].work == work_num])
            for work_num in set([p.work for p in self.pop])
        }

        # shopping is a bit more complicated because they are sets
        all_shopping = [p.shopping for p in self.pop]
        shopping_indexes = set()
        for shop in all_shopping:
            shopping_indexes = shopping_indexes | shop

        self.shopping = {
            shop_num: set([idx for idx in range(len(self.pop)) if shop_num in self.pop[idx].shopping])
            for shop_num in shopping_indexes
        }

    def set_vaccine_order(self):
        """
        Sets up the order that people get their vaccines. Ordered by the vaccine_score
        :return:
        """
        self.vaccine_order = sorted(range(len(self.pop)), key=lambda x: self.pop[x].vaccine_score)
