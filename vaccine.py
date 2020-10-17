from city import City
from person import Person
import random


class Vaccin meBase:
    def __init__(self, vaccine_name: str):
        self.name = vaccine_name

    def train(self):
        pass

    def assign_scores(self, city: City):
        for p in city.pop:
            self.assign_person_score(p)

    def assign_person_score(self, person: Person):
        raise NotImplemented()


class NoVaccine(VaccineBase):
    def __init__(self, vaccine_name: str):
        super().__init__(vaccine_name)

    def assign_person_score(self, person: Person):
        # Don't vaccinate anyone
        person.vaccine_score = -1


class RandomVaccine(VaccineBase):
    def __init__(self, vaccine_name: str):
        super().__init__(vaccine_name)

    def assign_person_score(self, person: Person):
        # Give everyone a random score (ie. first-come, first-served)
        person.vaccine_score = random.random()
