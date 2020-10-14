from city import City
import pathlib
import csv


def print_summary(c: City):
    print(f"City Simulator of Hamilton for {c.current_date.isoformat()}")
    print(f"\tStarting population: {c.starting_population}")
    print(f"\tFemale population: Female {c.sex_distribution:0.1%} / Male: {1-c.sex_distribution:0.1%}")
    print(f"\tCurrent population: {c.population}")
    print(f"\tTotal Recovered: {c.cumulative_recovered}")
    print(f"\tTotal Dead (Covid): {c.number_dead}")
    print(f"\tTotal sick with COVID: {c.cumulative_sick}")
    print(f"\tTotal never sick: {c.total_uninfected}")


if __name__ == '__main__':
    hamilton = City(size=1000)
    print_summary(hamilton)

    # Create the output directory
    output_dir = pathlib.Path(r'./output')
    if output_dir.exists() is False:
        output_dir.mkdir()
    print(output_dir.absolute())

    # for tick in range(1, 10):
    #     hamilton.run_timestep()
    #     print_summary(hamilton)

