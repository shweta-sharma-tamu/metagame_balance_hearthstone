import random
from typing import Set, Tuple


from metagame_balance.hearthstone.behaviour import TeamSelectionPolicy
from metagame_balance.hearthstone.datatypes.Constants import DEFAULT_TEAM_SIZE, MAX_TEAM_SIZE
from metagame_balance.hearthstone.datatypes.Objects import HsFullTeamView


class GUITeamSelectionPolicy(TeamSelectionPolicy):
    def __init__(self, selected_team_size: int = DEFAULT_TEAM_SIZE, full_team_size: int = MAX_TEAM_SIZE):
        import PySimpleGUI as sg
        self.selected_team_size = selected_team_size
        self.opp_title = sg.Text('Opponent Team:')
        self.opp = [[sg.Text('                                      ')] for _ in range(full_team_size)]
        self.team_title = sg.Text('Your Team:')
        self.team = [
            [sg.Text('                                      '),
             sg.Checkbox('Hs ' + str(i), size=(10, 1), default=False, enable_events=True)] for i in
            range(full_team_size)]
        self.select = sg.ReadFormButton('Select', bind_return_key=True)
        layout = [[self.opp_title]] + self.opp + [[self.team_title]] + self.team + [[self.select]]
        self.window = sg.Window('Pokemon Battle Engine', layout)
        self.window.Finalize()
        self.select.Update(disabled=True)

    def get_action(self, d: Tuple[HsFullTeamView, HsFullTeamView]) -> Set[int]:
        """

        :param d: (self, opponent)
        :return: idx list of selected pokemons
        """
        selected = []
        for item in self.team:
            item[1].Update(value=False)
        # opponent party
        opp_team = d[1]
        for i in range(opp_team.n_hss):
            hs = opp_team.get_hs_view(i)
            self.opp[i][0].Update(hs.type.name + ' ' + str(hs.hp) + ' HP')
        # my party
        my_team = d[0]
        for i in range(my_team.n_hss):
            hs = my_team.get_hs_view(i)
            self.team[i][0].Update(hs.type.name + ' ' + str(hs.hp) + ' HP')
        event, values = self.window.read()
        while event != self.select.get_text():
            if event not in selected:
                selected.append(event)
            else:
                selected.remove(event)
            self.select.Update(disabled=self.selected_team_size != len(selected))
            event, values = self.window.read()
        return set(selected)

    def close(self):
        self.window.close()


class RandomTeamSelectionPolicy(TeamSelectionPolicy):

    def __init__(self, teams_size: int = DEFAULT_TEAM_SIZE, selection_size: int = DEFAULT_TEAM_SIZE):
        self.teams_size = teams_size
        self.selection_size = selection_size

    def get_action(self, d: Tuple[HsFullTeamView, HsFullTeamView]) -> Set[int]:
        """

        :param d: (self, opponent)
        :return: idx list of selected pokemons
        """
        ids = [i for i in range(self.teams_size)]
        random.shuffle(ids)
        return set(ids[:self.selection_size])

    def close(self):
        pass


class FirstEditionTeamSelectionPolicy(TeamSelectionPolicy):

    def get_action(self, d: Tuple[HsFullTeamView, HsFullTeamView]) -> Set[int]:
        """
        Teams are selected as they are.

        :param d: (self, opponent)
        :return: idx list of selected pokemons
        """
        return {0, 1, 2}

    def close(self):
        pass
