from person import Person
import typing as t
from datetime import date, timedelta
import random


class City:
    def __init__(self, name: str, size: int = 1000, initial_sick: float = 0.10):
        self.name = name
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
            if random.random() < initial_sick:
                # Create a sick person
                days_since_infection = random.randint(0, 40)
                sick_day = self.start_date - timedelta(days=days_since_infection)
                person.infect(sick_day)
                for j in range(days_since_infection):
                    person.update_health(sick_day + timedelta(days=j))
                if person.is_alive is False:
                    person.recover(sick_day + timedelta(days=days_since_infection))
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
    def num_dead(self) -> int:
        return sum([not p.is_alive for p in self.pop])

    @property
    def num_sick(self) -> int:
        return sum([p.is_currently_sick for p in self.pop])

    @property
    def num_recovered(self) -> int:
        return sum([p.is_recovered for p in self.pop])

    @property
    def num_vulnerable(self) -> int:
        return sum([p.is_vulnerable for p in self.pop])

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

    def get_sick_people(self) -> t.List[int]:
        """
        Return the index of all the people who are contagious
        :return:
        """
        return [idx for idx, p in enumerate(self.pop) if p.is_infected]

    def step1_work(self, interactions: t.List[int], sick_people: t.List[int]):
        """
        Update all the interactions a sick person has with everyone else
        :param interactions:
        :param sick_people:
        :return:
        """
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            if not sick_person.in_quarantine:
                continue  # Can't get people sick at work if you are in quarantine
            for other_idx, work_person in enumerate(self.pop):
                if work_person.is_vulnerable and work_person.work == sick_person.workplace_id:
                    interactions[other_idx] += 10

    def step2_home(self, interactions: t.List[int], sick_people: t.List[int]):
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            for other_idx, home_person in enumerate(self.pop):
                if home_person.is_vulnerable and home_person.household == sick_person.household:
                    interactions[other_idx] += 40

    def step3_shopping(self, interactions: t.List[int], sick_people: t.List[int]):
        for sick_idx in sick_people:
            sick_person = self.pop[sick_idx]
            sick_person_places = sick_person.shopping | {sick_person.workplace_id}
            for other_idx, shop_person in enumerate(self.pop):
                if shop_person.is_vulnerable & len(sick_person_places) > 0:
                    interactions[other_idx] += 5

    def step4_vaccine(self):
        vaccines_total = 1000
        dates_available = [self.start_date + timedelta(days=30*(i+1)) for i in range(10)]
        vaccines_available = vaccines_total // len(dates_available)
        if self.current_date not in dates_available:
            return
        vaccines_given = 0
        person_scores = [p.vaccine_score for p in self.pop if p.is_alive and p.is_vaccinated is False and p.vaccine_score >= 0]
        person_scores.sort()
        if len(person_scores) < vaccines_available:
            # everyone gets a vaccine
            for person in self.pop:
                if person.is_alive and person.is_vaccinated is False and person.vaccine_score >= 0:
                    person.vaccinate()
        else:
            # only people with a score below a certain value get vaccinated
            max_score_to_vaccinate = person_scores[vaccines_available]
            for person in self.pop:
                if person.is_alive and person.is_vaccinated is False and 0 <= person.vaccine_score < max_score_to_vaccinate:
                    person.vaccinate()
                vaccines_given += 1
                if vaccines_given > vaccines_available:
                    break

    def step5_health_update(self, interactions: t.List[int]):
        for idx, person in enumerate(self.pop):
            if person.is_vulnerable:
                num_interactions = interactions[idx]
                chance_of_sickness = (1+0.00001) ** num_interactions - 1
                chance_of_sickness *= 1 - person.covid_immunity           # Adjust for immunity
                if random.random() < chance_of_sickness:
                    person.infect(self.current_date)

            # update their health
            person.update_health(self.current_date)
