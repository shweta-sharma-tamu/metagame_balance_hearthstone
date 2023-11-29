import numpy as np
from metagame_balance.hearthstone.datatypes.Objects import HsTemplate, Hs
from metagame_balance.hearthstone.datatypes.Constants import STATS_OPT_2_PER_MOVE
from metagame_balance.hearthstone.datatypes.Constants import NUM_TYPES


def mark_with_pokemon(state, hs, hs_pos, state_dim: int, team_size: int):
    """
    Function marks team and the new one vector
    """

    def get_moves(hs):
        if isinstance(hs, HsTemplate):
            return hs.move_roster
        elif isinstance(hs, Hs):
            return hs.moves
        else:
            raise Exception("Unrecognized hs object type: " + str(hs))

    def type_to_idx(type_):
        return int(type_)

    idx_to_move_stat_map = {0: lambda hs: hs.power, 1: lambda hs: hs.acc,
                            2: lambda hs: hs.max_pp}
    stats_per_hs = state_dim // team_size
    base_idx = hs_pos * stats_per_hs
    state[base_idx] = hs.max_hp
    state[base_idx + 1 + type_to_idx(hs.type)] = 1
    base_idx += 1 + NUM_TYPES

    for i, move in enumerate(get_moves(hs)):
        for j in range(len(idx_to_move_stat_map)):
            move_idx = i * STATS_OPT_2_PER_MOVE + j
            state[base_idx + move_idx] = idx_to_move_stat_map[j](move)
        state[base_idx + move_idx + type_to_idx(move.type) + 1] = 1
        # print(hs.max_hp, hs.type, move.power, move.acc, move.max_pp, move.type, int(move.type))
    return state


class HSTeam():
    def __init__(self):
        self.hss = []

    def __getitem__(self, idx: int):
        return self.hss[idx]

    def __len__(self):
        return len(self.hss)

    def mark(self, hs_idx: int):
        self.hss.append(hs_idx)


def predict(u, hs_list, state_dim: int, team_size: int):
    """
    U is the value function in HS
    """
    hs_list = hs_list

    def batch_predictor(teams):
        x = np.zeros((len(teams), state_dim))

        for i, team in enumerate(teams):
            for j in range(len(team)):
                mark_with_pokemon(x[i], hs_list[team[j]], j, state_dim, team_size)

        return u.predict(x)

    return batch_predictor
