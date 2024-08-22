# Fine Material Mining
The purpose of this guide is to explore the optmial setup for mining fine materials in walkscape.
The final objective is to optimize the amount of steps needed to get fine materials in the bank. Before that let's focus on a slightly easier goal of optimizing the amount of fine materials per step when mining. 

Due to the low probability of getting fine materials, the amount of fine material per step is going to be very small. For convenience it is much nicer to compare the inverse, the amount of steps per fine material, which we will want to minimize.

## Steps per Fine Material
### Related mechanics
#### Work Efficiency
The relation of work efficiency (WE) when finding fine materials is simple. The more WE you have, the less steps it takes for you to get each ore, which increases your material/step.

The amount of work efficiency increases that will help you in your efforts differs based on the activity you're doing. Additional work efficiency beyond the limit will not increase your effectiveness and is wasted.

The different required levels, and maximum work efficiencies for mining activities are as follows:
- Mine copper ore - lvl 1 - 50%
- Surface salt mining - lvl 1 - 50%
- Mine tin ore - lvl 10 - 60%
- Mine iron ore - lvl 20 - 60%
- Gold panning - lvl 15 - 60%
- Stone quarrying - lvl 1 - 60%
- Mine coal - lvl 30 - 80%
- Mine tarsilium ore - lvl 40 - 90%
- Mine farganite ore - lvl 50 - 100%
- Spelunking lvl - 50 - 150%

There are two sources of work efficiency
- Gear
- Mining Skill Levels

Work efficiency from gear is either global work efficiency or work efficiency while mining.    
Mining skill levels give +1.25% work efficiency per skill level above the required level of the activity, up to 20 levels or +25% work efficiency.
All sources of work efficiency are added together.

#### Minus steps required
Gear with -X steps required can reduce the steps required per action even further beyong the limit that work efficiency allows for.

#### Fine Material Finding
Each time a material is rolled as a reward, it has a chance of dropping as a fine material instead. The base chance of a fine material dropping is ``1 in 200``.
The chance of dropping fine materials can be increased with gear that has increased Fine Material Finding (FMF) chance. 

Each source of FMF is added together, and used to multiply the fine material drop chance. With total +100% FMF the calculation would be as follows.
```
fine_material_drop_chance = base_chance * (1 + total_FMF)
fine_material_drop_chance = 1/200 * (1 + 1)
fine_material_drop_chance = 2/200 = 1/100
```

The amount of Fine Material Finding a player can have is not capped.

#### Double Rewards
Each time a player finishes an action, they roll each of the activity's related loot tables. An activity can have multiple loot tables. For Mining Tarsilium Ore there are three: the ore loot table, the mining chest loot table, and the realm's gem loot table. 

If the player has gear that adds chance for double rewards (DR), before rolling a loot table, the game checks if DR procs. If it does, the player rolls said loot table twice.

In the case of the tarsillium ore loot table, which has a 100% chance of dropping tarsilium ore, if the DR procs, the player will receive two tarsilium ore instead of one from their single action.

#### Double Action
Similarly to Double Rewards, Double Action (DA) is checked when the player finishes an action. If DA procs, the player will complete a second action for free. The second action will receive all the same benefits as the first action, and give the player xp and reward rolls. 

DR can proc on both actions, potentially giving the player 4 reward rolls of a loot table on a single action.

With source of DA and DR, we can calculate the average amount of reward rolls per action as follows:
``Reward rolls = (1 + DA) * (1 + DR)``

For a player with +20% DR and DA, they will receive an average of `(1 + 0.2) * (1 + 0.2) = 1.44` reward rolls per action for each loot table.

