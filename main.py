from city import City
import pathlib
import time
import csv


def print_summary(c: City):
    print(f"City Simulator of Hamilton for {c.current_date.isoformat()}")
    print(f"\tStarting population: {c.starting_population}")
    print(f"\tFemale population: Female {c.sex_distribution:0.1%} / Male: {1-c.sex_distribution:0.1%}")
    print(f"\tCurrent population: {c.population}")
    print(f"\tSick: {c.num_sick}")
    print(f"\tRecovered: {c.num_recovered}")
    print(f"\tVulnerable: {c.num_vulnerable}")
    print(f"\tDead: {c.num_dead}")


def create_summary_dictionary(c: City):
    res = {
        'start_date': c.start_date.isoformat(),
        'current_date': c.current_date.isoformat(),
        'starting_pop': c.starting_population,
        'current_pop': c.population,
        'female_pop_pct': c.sex_distribution,
        'male_pop_pct': 1-c.sex_distribution,
        'sick': c.num_sick,
        'recovered': c.num_recovered,
        'vulnerable': c.num_vulnerable,
        'dead': c.num_dead
    }
    return res


if __name__ == '__main__':
    start_time = time.perf_counter()
    newmarket = City(size=1000)
    print_summary(newmarket)

    # Create the output directory
    output_dir = pathlib.Path(r'./output')
    if output_dir.exists() is False:
        output_dir.mkdir()
    print(output_dir.absolute())

    # Output data
    csv_file_path = output_dir / 'newmarket.csv'
    with csv_file_path.open('w', newline='') as csv_file:
        info = create_summary_dictionary(newmarket)
        writer = csv.DictWriter(csv_file, fieldnames=list(info.keys()))
        writer.writeheader()    # Write the header
        writer.writerow(info)   # Write the initial data

        for tick in range(1, 365):
            newmarket.run_timestep()
            writer.writerow(create_summary_dictionary(newmarket))

    print_summary(newmarket)
    print(f"Total time: {time.perf_counter() - start_time:0.4f} seconds")
