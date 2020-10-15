from city import City
from vaccine import VaccineBase, NoVaccine, RandomVaccine
from ai_vaccine import VaccineAI
from settings import *
import copy
import time
import csv


def create_summary_dictionary(c: City):
    res = {
        'start_date': c.start_date.isoformat(),
        'current_date': c.current_date.isoformat(),
        'starting_pop': c.starting_population,
        'current_pop': c.population,
        'female_pop_pct': c.female_pct,
        'male_pop_pct': 1-c.female_pct,
        'sick': c.num_sick,
        'recovered': c.num_recovered,
        'uninfected': c.num_uninfected,
        'dead': c.num_dead,
        'vacinated': c.num_vaccinated,
        'wasted_vaccine': c.num_wasted_vaccines,
        'mortality_rate': c.num_dead / max(1, (c.num_dead + c.num_recovered)),
        'infection_rate': (c.num_recovered + c.num_dead + c.num_sick) / max(1, c.starting_population),
        'teacher_sick_rate': c.teachers_pct_sick,
        'hospital_worker_sick_rate': c.hospital_worker_pct_sick,
        'frontline_worker_sick_rate': c.frontline_worker_pct_sick
    }
    return res


def trial(vaccine: VaccineBase, city: City, trial_num: int, days: int):
    trial_start_time = time.perf_counter()
    # assign the scores
    vaccine.assign_scores(city)

    # Create the output directory
    if output_dir.exists() is False:
        output_dir.mkdir()

    # Output data
    csv_file_path = output_dir / f'{city.name}-{vaccine.name}-{trial_num}.csv'
    with csv_file_path.open('w', newline='') as csv_file:
        # Create the file and get the initial data
        info = create_summary_dictionary(city)
        writer = csv.DictWriter(csv_file, fieldnames=list(info.keys()))
        writer.writeheader()    # Write the header
        writer.writerow(info)   # Write the initial data

        # Run the simulation for this many days
        for tick in range(1, days):
            city.run_timestep()
            writer.writerow(create_summary_dictionary(city))

    print(
        f"\tCompleted trial {city.name} - {vaccine.name} #{trial_num}: "
        f"{time.perf_counter() - trial_start_time:0.2f} sec")


if __name__ == '__main__':
    print('COVID 19 Simulator')
    city_size = 1000
    initial_sick = 100
    days = 180
    train_ai = False

    start_time = time.perf_counter()
    random_vaccine = RandomVaccine('random_vaccine')
    no_vaccine = NoVaccine('no_vaccine')
    ai_vaccine = VaccineAI('ai')
    if train_ai:
        ai_vaccine.train(max_cycles=100)
        ai_vaccine.save_nn()
    else:
        ai_vaccine.load_nn()

    for i in range(1):
        trial_city = City(name='newmarket', size=city_size, initial_sick=initial_sick)
        trial(random_vaccine, copy.deepcopy(trial_city), trial_num=i, days=days)
        trial(no_vaccine, copy.deepcopy(trial_city), trial_num=i, days=days)
        trial(ai_vaccine, copy.deepcopy(trial_city), trial_num=i, days=days)
    print(f"Completed trials: {time.perf_counter() - start_time:0.2f} seconds")
