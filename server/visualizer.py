from os import name, system
from typing import Dict


class IGameStateVisualizer:

    def visualize(self, state_dict: Dict):
        pass


class NoVisualizer(IGameStateVisualizer):

    def visualize(self, state_dict: Dict):
        pass


class TerminalPrinter(IGameStateVisualizer):
    def __init__(self, clear_screen: bool) -> None:
        super().__init__()
        self.clear_screen = clear_screen

    def visualize(self, state_dict: Dict):
        pass
    #     if self.clear_screen:
    #         _clear_screen()

    #     print('-' * 10)
    #     self._print_board(state_dict)
    #     print('-' * 10)

    #     current_player = state_dict.players[state_dict.current_player_index]
    #     print(f'Current player: {current_player.name}')
    #     print('-' * 10)

    # # def __repr__(self) -> str:
    # #     steps = []
    # #     entrances = {self.home_entrance_location(player): player.name[0] for player in self.players}
    # #     print(' '.join([f'{x:02d}' for x in range(len(self.state_dict))]))
    # #     for index, step in enumerate(self.state_dict):
    # #         if isinstance(step, EmptyPiece) and index in entrances.keys():
    # #             representation = f'{entrances[index]}H'
    # #         else:
    # #             representation = step.name
    # #         steps.append(representation)
    # #     return ' '.join(steps)

    # def _print_board(self, state_dict: GameState):
    #     route = str(state_dict.route)
    #     homes = list(zip(*[str(home).split(' ') for home in state_dict.homes]))
    #     print(route)
    #     spaces = '  ' * (GameState.PLAYER_LANE_SIZE - 1) + ' ' * GameState.PLAYER_LANE_SIZE
    #     for home in homes:
    #         home_str = spaces[:-1] + spaces.join(home)
    #         print(home_str)


# define our clear function
def _clear_screen():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
