from metagame_balance.hearthstone.datatypes.Objects import HsMove
from metagame_balance.hearthstone.datatypes.Types import HsType, HsStatus, WeatherCondition, HsStat, HsEntryHazard

# Struggle
Struggle = HsMove(max_pp=0, name="Struggle")

# Normal Moves
Recover = HsMove(0., 1., 5, HsType.NORMAL, "Recover", recover=80., target=0, prob=1.)
DoubleEdge = HsMove(120., 1., 10, HsType.NORMAL, "Double-Edge", recover=-40., prob=1.)
ExtremeSpeed = HsMove(80., 1., 10, HsType.NORMAL, "Extreme Speed", priority=True)
Slam = HsMove(80., .75, 20, HsType.NORMAL, "Slam", status=HsStatus.PARALYZED, prob=1 / 3)
Tackle = HsMove(40., 1., 20, HsType.NORMAL, "Tackle")

# Fire Moves
SunnyDay = HsMove(0., 1., 5, HsType.FIRE, "Sunny Day", weather=WeatherCondition.SUNNY, prob=1.)
FireBlast = HsMove(110., .85, 5, HsType.FIRE, "Fire Blast", status=HsStatus.BURNED, prob=.3)
Flamethrower = HsMove(90., 1., 15, HsType.FIRE, "Flamethrower", status=HsStatus.BURNED, prob=.1)
Ember = HsMove(40., 1., 20, HsType.FIRE, "Ember", status=HsStatus.BURNED, prob=.1)

# Water Moves
RainDance = HsMove(0., 1., 5, HsType.WATER, "Rain Dance", weather=WeatherCondition.RAIN, prob=1.)
HydroPump = HsMove(110., .8, 5, HsType.WATER, "Hydro Pump")
AquaJet = HsMove(40., 1., 20, HsType.WATER, "Aqua Jet", priority=True)
BubbleBeam = HsMove(65., 1., 20, HsType.WATER, "Bubble Beam", stat=HsStat.SPEED, stage=-1, prob=.1)

# Electric Moves
ThunderWave = HsMove(0., 1., 20, HsType.ELECTRIC, "Thunder Wave", status=HsStatus.PARALYZED, prob=1.)
Thunder = HsMove(110., .7, 10, HsType.ELECTRIC, "Thunder", status=HsStatus.PARALYZED, prob=.3)
Thunderbolt = HsMove(90., 1., 15, HsType.ELECTRIC, "Thunderbolt", status=HsStatus.PARALYZED, prob=.1)
ThunderShock = HsMove(40., 1., 20, HsType.ELECTRIC, "Thunder Shock", status=HsStatus.PARALYZED, prob=.1)

# Grass Moves
Spore = HsMove(0., 1., 5, HsType.GRASS, "Spore", status=HsStatus.SLEEP, prob=1)
GigaDrain = HsMove(75., 1., 15, HsType.GRASS, "Giga Drain", recover=30., prob=1.)
RazorLeaf = HsMove(55., .95, 20, HsType.GRASS, "Razor Leaf")
EnergyBall = HsMove(90., 1., 10, HsType.GRASS, "Energy Ball", stat=HsStat.DEFENSE, stage=-1, prob=.1)

# Ice Moves
Hail = HsMove(0., 1., 5, HsType.ICE, "Hail", weather=WeatherCondition.HAIL)
Blizzard = HsMove(110., .7, 5, HsType.ICE, "Blizzard", status=HsStatus.FROZEN, prob=.1)
IceBeam = HsMove(90., 1., 10, HsType.ICE, "Ice Beam", status=HsStatus.FROZEN, prob=.1)
IceShard = HsMove(40., 1., 20, HsType.ICE, "Ice Shard", priority=True)

# Fighting Moves
BulkUp = HsMove(0., 1., 5, HsType.FIGHT, "Bulk Up", stat=HsStat.ATTACK, stage=2, target=0, prob=1.)
MachPunch = HsMove(40., 1., 20, HsType.FIGHT, "Mach Punch", priority=True)
CloseCombat = HsMove(120., 1., 5, HsType.FIGHT, "Close Combat", stat=HsStat.DEFENSE, stage=-2, target=0, prob=1.)
DynamicPunch = HsMove(100., .5, 5, HsType.FIGHT, "Dynamic Punch", status=HsStatus.CONFUSED, prob=1.)

# Poison Moves
Poison = HsMove(0., 1., 5, HsType.POISON, "Poison", status=HsStatus.POISONED, prob=1.)
GunkShot = HsMove(110., .8, 5, HsType.POISON, "Gunk Shot", status=HsStatus.POISONED, prob=.3)
PoisonJab = HsMove(80., 1., 5, HsType.POISON, "Poison Jab", status=HsStatus.POISONED, prob=.3)
AcidSpray = HsMove(40., 1., 20, HsType.POISON, "Acid Spray", stat=HsStat.DEFENSE, stage=-2, prob=1.)

# Ground Moves
Spikes = HsMove(0., 1., 20, HsType.GROUND, "Spikes", hazard=HsEntryHazard.SPIKES, prob=1.)
Earthquake = HsMove(100., 1., 10, HsType.GROUND, "Earthquake")
MudShot = HsMove(55., .95, 15, HsType.GROUND, "Mud Shot", stat=HsStat.SPEED, stage=-1, prob=1.)
EarthPower = HsMove(90., 1., 10, HsType.GROUND, "Earth Power", stat=HsStat.DEFENSE, stage=-1, prob=.1)

# Flying Moves
Roost = HsMove(0., 1., 5, HsType.FLYING, "Roost", recover=80., target=0, prob=1.)
Chatter = HsMove(65., 1., 20, HsType.FLYING, "Chatter", status=HsStatus.CONFUSED, prob=1.)
Hurricane = HsMove(110., .7, 10, HsType.FLYING, "Hurricane", status=HsStatus.CONFUSED, prob=.3)
WingAttack = HsMove(60., 1., 20, HsType.FLYING, "Wing Attack")

# Psychic Moves
CalmMind = HsMove(0., 1., 5, HsType.PSYCHIC, "Calm Mind", stat=HsStat.DEFENSE, stage=2, target=0, prob=1.)
Psychic = HsMove(90., 1., 10, HsType.PSYCHIC, "Psychic", stat=HsStat.DEFENSE, stage=-1, prob=.1)
PsychoBoost = HsMove(140., .9, 5, HsType.PSYCHIC, "Psycho Boost", stat=HsStat.DEFENSE, stage=-2, target=0, prob=.1)
Psybeam = HsMove(65., 1., 10, HsType.PSYCHIC, "Psybeam", status=HsStatus.CONFUSED, prob=.1)

# Bug Moves
StringShot = HsMove(0., 1., 5, HsType.BUG, "String Shot", stat=HsStat.SPEED, stage=-1)
BugBuzz = HsMove(90., 1., 10, HsType.BUG, "Bug Buzz", stat=HsStat.DEFENSE, stage=-1, prob=.1)
LeechLife = HsMove(80., 1., 10, HsType.BUG, "Leech Life", recover=40., prob=1.)

# Rock Moves
Sandstorm = HsMove(0., 1., 5, HsType.ROCK, "Sandstorm", weather=WeatherCondition.SANDSTORM, prob=1.)
PowerGem = HsMove(80., 1., 20, HsType.ROCK, "Power Gem")
RockTomb = HsMove(60., .95, 15, HsType.ROCK, "Rock Tomb", stat=HsStat.SPEED, stage=-1, prob=1.)
StoneEdge = HsMove(100., .8, 5, HsType.ROCK, "Stone Edge")

# Ghost Moves
NightShade = HsMove(0., 1., 10, HsType.GHOST, "Night Shade", fixed_damage=40., prob=1.)
ShadowBall = HsMove(80., 1., 15, HsType.GHOST, "Shadow Ball", stat=HsStat.DEFENSE, stage=-1, prob=.2)
ShadowSneak = HsMove(40., 1., 20, HsType.GHOST, "Mach Punch", priority=True)

# Dragon Moves
DragonRage = HsMove(0., 1., 10, HsType.DRAGON, "Dragon Rage", fixed_damage=40., prob=1.)
DracoMeteor = HsMove(130., .9, 5, HsType.DRAGON, "Draco Meteor", stat=HsStat.ATTACK, stage=-2, target=0, prob=1.)
DragonBreath = HsMove(60., 1., 20, HsType.DRAGON, "Dragon Breath", status=HsStatus.PARALYZED, prob=1.)
Outrage = HsMove(120., 1., 10, HsType.DRAGON, "Outrage", status=HsStatus.CONFUSED, target=0, prob=1.)

# Dark Moves
NastyPlot = HsMove(0., 1., 5, HsType.DARK, "Nasty Plot", stat=HsStat.ATTACK, stage=2, target=0, prob=1.)
Crunch = HsMove(80., 1., 15, HsType.DARK, "Crunch", stat=HsStat.DEFENSE, stage=-1, prob=.2)
Snarl = HsMove(55., .95, 15, HsType.DARK, "Snarl", stat=HsStat.ATTACK, stage=-1, prob=1.)

# Steel Moves
IronDefense = HsMove(0., 1., 5, HsType.STEEL, "Iron Defense", stat=HsStat.DEFENSE, stage=2, target=0, prob=1.)
IronTail = HsMove(100., .75, 15, HsType.STEEL, "Iron Tail", stat=HsStat.DEFENSE, stage=-1, prob=.3)
SteelWing = HsMove(70., .9, 20, HsType.STEEL, "Steel Wing", stat=HsStat.DEFENSE, stage=2, target=0, prob=.1)
BulletPunch = HsMove(40., 1., 20, HsType.STEEL, "Bullet Punch", priority=True)

# Fairy Moves
SweetKiss = HsMove(0., .75, 5, HsType.FAIRY, "Sweet Kiss", status=HsStatus.CONFUSED, prob=1.)
PlayRough = HsMove(90., .9, 10, HsType.FAIRY, "Play Rough", stat=HsStat.ATTACK, stage=-1, prob=.1)
Moonblast = HsMove(95., 1., 15, HsType.FAIRY, "Moonblast", stat=HsStat.ATTACK, stage=-1, prob=.3)

# Standard Move Pool
STANDARD_MOVE_ROSTER = [Recover, DoubleEdge, ExtremeSpeed, Slam, Tackle, SunnyDay, FireBlast, Flamethrower,
                        Ember, RainDance, HydroPump, AquaJet, BubbleBeam, ThunderWave, Thunder, Thunderbolt,
                        ThunderShock, Spore, GigaDrain, RazorLeaf, EnergyBall, Hail, Blizzard, IceBeam,
                        IceShard, BulkUp, MachPunch, CloseCombat, DynamicPunch, Poison, GunkShot, PoisonJab,
                        AcidSpray, Spikes, EarthPower, Earthquake, MudShot, Roost, Chatter, Hurricane,
                        WingAttack, CalmMind, Psychic, PsychoBoost, Psybeam, StringShot, BugBuzz, LeechLife,
                        Sandstorm, PowerGem, RockTomb, StoneEdge, NightShade, ShadowBall, ShadowSneak, DragonRage,
                        DracoMeteor, DragonBreath, Outrage, NastyPlot, Crunch, Snarl, IronDefense, IronTail, SteelWing,
                        BulletPunch, SweetKiss, PlayRough, Moonblast]
