import concurrent.futures
from random import uniform

def roll(chance):
  return uniform(0,1) <= chance

def action(chance, DA=0, DR=0):
  action_count = 2 if roll(DA) else 1
  reward_count = sum([2 if roll(DR) else 1 for i in range(action_count)])
  return any([roll(chance) for i in range(reward_count)])

def until_drop(chance, DA, DR, step_count):
  actions = 0
  steps = 0
  while True:
    actions += 1
    steps += step_count
    if action(chance, DA, DR):
      return actions, steps

def simulate(runs, chance, double_action, double_rewards, step_count):
  results = [
    until_drop(chance, double_action, double_rewards, step_count) 
    for i in range(runs)
  ]
  s = sorted(results, key=lambda x: x[0])
  actions, steps = zip(*s)
  minimum = s[0]
  maximum = s[-1]
  average = [sum(actions)//runs, sum(steps)//runs]
  median = s[runs//2]

  return minimum, maximum, average, median

def simulate_run(chance, double_action, double_rewards, step_count):
    return until_drop(chance, double_action, double_rewards, step_count)

def simulate_parallel(runs, chance, double_action, double_rewards, step_count):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(simulate_run,
                                    (chance for _ in range(runs)),
                                    (double_action for _ in range(runs)),
                                    (double_rewards for _ in range(runs)),
                                    (step_count for _ in range(runs))
        ))
    s = sorted(results, key=lambda x: x[0])
    actions, steps = zip(*s)
    minimum = s[0]
    maximum = s[-1]
    average = [sum(actions)//runs, sum(steps)//runs]
    median = s[runs//2]

    return minimum, maximum, average, median

def main():
  chance = 1/3754
  DA = 0.05
  DR = 0.13
  step_count = 41
  runs = 10000

  results = simulate_parallel(runs, chance, DA, DR, step_count)
  [minimum, maximum, average, median] = results

  pad_1 = len(str(maximum[0]))
  pad_2 = len(str(maximum[1]))

  print()
  print(f"           drop chance: 1 / {int(1/chance)}")
  print(f"         double action: {DA}")
  print(f"        double rewards: {DR}")
  print(f"          steps/action: {step_count}")

  print(f"\n         simulating {runs} runs:")
  print(f"     min: {minimum[0]:>{pad_1}} actions, {minimum[1]:>{pad_2}} steps")
  print(f"     max: {maximum[0]:>{pad_1}} actions, {maximum[1]:>{pad_2}} steps")
  print(f" average: {average[0]:>{pad_1}} actions, {average[1]:>{pad_2}} steps")
  print(f"  median: {median[0]:>{pad_1}} actions, {median[1]:>{pad_2}} steps")
  print()

if __name__ == '__main__':
  main()