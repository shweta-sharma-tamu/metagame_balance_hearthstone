from multiprocessing.connection import Client

from metagame_balance.hearthstone.behaviour.BattlePolicies import RandomBattlePolicy
from metagame_balance.hearthstone.engine.HsBattleEnv import HsBattleEnv
from metagame_balance.hearthstone.util.generator.HsTeamGenerators import RandomTeamGenerator

address = ('localhost', 6000)
gen = RandomTeamGenerator()
full_team0 = gen.get_team()
full_team1 = gen.get_team()
conn = Client(address, authkey='HS AI'.encode('utf-8'))
env = HsBattleEnv((full_team0.get_battle_team([0, 1, 2]), full_team1.get_battle_team([0, 1, 2])), debug=True,
                   conn=conn)
env.reset()
t = False
a0 = RandomBattlePolicy()
a1 = RandomBattlePolicy()
ep = 0
n_battles = 3
while ep < n_battles:
    s = env.reset()
    v = env.game_state_view
    env.render(mode='ux')
    ep += 1
    while not t:
        o0 = s[0] if a0.requires_encode() else v[0]
        o1 = s[1] if a1.requires_encode() else v[1]
        a = [a0.get_action(o0), a1.get_action(o1)]
        s, _, t, v = env.step(a)
        env.render(mode='ux')
    t = False
env.close()
