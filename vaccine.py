from city import City
from person import Person
import random


class VaccineBase:
    def __init__(self, c: City):
        self.city = c

    def assign_scores(self):
        for p in self.city.pop:
            self.assign_person_score(p)

    def assign_person_score(self, person: Person):
        pass


class NoVaccine(VaccineBase):
    def __init__(self, c: City):
        super().__init__(c)

    def assign_person_score(self, person: Person):
        person.vaccine_score = -1


class RandomVaccine(VaccineBase):
    def __init__(self, c: City):
        super().__init__(c)

    def assign_person_score(self, person: Person):
        person.vaccine_score = random.random()
