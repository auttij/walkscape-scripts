from random import uniform
from math import ceil
from statistics import mode, mean, median

DISTANCES = {
    "none": 0,
    "extremelyNear": 160,
    "veryNear": 280,
    "near": 390,
    "veryShort": 450,
    "short": 550,
    "lowModerate": 650,
    "moderate": 800,
    "moderateHigh": 1000,
    "lowHigh": 1300,
    "high": 1600,
    "veryHigh": 2000,
    "extensive": 3000,
    "veryExtensive": 4500,
    "extreme": 6000,
    "endless": 10000,
}


def get_distance(distance, modifier):
    assert distance in DISTANCES, f"No such distance {distance}"
    return int(DISTANCES[distance] * modifier)


def roll(chance):
    return uniform(0, 1) <= chance


def action(DA=0):
    return 2 if roll(DA) else 1


def simulate_travel(distance, modifier, work_efficiency, double_action, steps_modifier):
    work = get_distance(distance, modifier)
    base_steps = work / (1 + work_efficiency / 100)
    action_steps = ceil(max(5, base_steps / 10 + steps_modifier))

    steps_taken = 0
    progress = 0
    while progress < 10:
        progress += action(double_action / 100)
        steps_taken += action_steps

    DA_procs = 10 - (steps_taken // action_steps)
    return steps_taken, DA_procs


def print_stats(runs, work_efficiency, double_action, steps_modifier):
    sorted_runs = sorted(runs)
    count = len(runs)

    print(
        f"\n{work_efficiency} work efficiency, {double_action} DA, {steps_modifier} steps mod"
    )
    print(f"min: {sorted_runs[0]}")
    print(f"median: {median(runs)}")
    print(f"max: {sorted_runs[-1]}")
    print(f"mean {mean(runs)}")
    print(f"mode {mode(runs)}")
    print()


def simulate_runs(
    runs, distance, modifier, work_efficiency, double_action, steps_modifier
):
    return (
        simulate_travel(
            distance, modifier, work_efficiency, double_action, steps_modifier
        )
        for i in range(runs)
    )


def main():

    # for key in DISTANCES.keys():
    key = "moderate"
    multi = 1
    count = 500
    WE = 65

    print()
    print(f"{key}: {get_distance(key, multi)} base steps")
    print(f"simulating {count} runs")
    route = [key, multi]

    stats_1 = route + [WE, 15, -5]
    runs, DA_procs_1 = zip(*list(simulate_runs(count, *stats_1)))
    print_stats(runs, *stats_1[2:])

    stats_2 = route + [WE, 45, 5]
    runs, DA_procs_2 = zip(*list(simulate_runs(count, *stats_2)))
    print_stats(runs, *stats_2[2:])
    print("----------------------------")

    print("\nDA Procs")
    print_stats(DA_procs_1, *stats_1[2:])
    print_stats(DA_procs_2, *stats_2[2:])


if __name__ == "__main__":
    main()
