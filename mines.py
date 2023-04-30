"""
Entry point and CLI implementation for terminal-mines.
"""

import click

from game_logic import random_minefield, GameState, input_loop, render

DIFFICULTY_PRESETS = {
    "balanced": (35, 20, 15),
    "challenging": (70, 25, 20),
    "easy": (10, 8, 8),
    "intermediate": (40, 16, 16),
    "expert": (99, 16, 30)
}


class DifficultyParamType(click.ParamType):
    """
    Converts the provided difficulty string into the 3 args expected by random_minefield().
    """
    def convert(self, value, param, ctx):
        if value in DIFFICULTY_PRESETS:
            return DIFFICULTY_PRESETS[value]
        elif "," not in value:
            self.fail("'{}' is not a valid difficulty name".format(value), param, ctx)
        else:
            try:
                args = tuple(map(int, value.split(",")))

                if len(args) != 3:
                    raise ValueError
                elif args[0] < 0 or args[1] < 0 or args[2] < 0:
                    raise ValueError
                elif args[1] > 50 or args[2] > 50:
                    self.fail("the game board cannot be larger than 50 cells on either side", param, ctx)
                elif args[0] > args[1] * args[2]:
                    self.fail("{} mines cannot fit in a board size of {} by {}".format(*args), param, ctx)

                return args
            except ValueError:
                self.fail("a custom difficulty must be made of 3 positive integers separated by commas", param, ctx)

class KeyHandler:
    def __init__(self, minefield, ctx):
        self.minefield = minefield
        self.ctx = ctx
    def handle_key(self, key):
        if key == "w":
            self.minefield.y = (self.minefield.y - 1) % self.minefield.height
        elif key == "s":
            self.minefield.y = (self.minefield.y + 1) % self.minefield.height
        elif key == "a":
            self.minefield.x = (self.minefield.x - 1) % self.minefield.width
        elif key == "d":
            self.minefield.x = (self.minefield.x + 1) % self.minefield.width
        elif key == "e" or key == "'":
            self.minefield.flag_cell(self.minefield.x, self.minefield.y)
        elif key == "\n" or key == " ":
            self.minefield.reveal_cell(self.minefield.x, self.minefield.y)
        render(self.minefield)
        if self.minefield.state != GameState.IN_PROGRESS:
            self.ctx.exit(0)

@click.command()
@click.pass_context
@click.argument("difficulty", default="balanced", type=DifficultyParamType())
def main(ctx, difficulty):
    """
    Terminal Mines

    A command-line variant of Minesweeper in Python.

    \b
    Controls:
    - WASD or arrow keys to move the cursor
    - Enter or space to reveal the current cell
    - e or ' to place a flag
    - ESC to quit

    DIFFICULTY can either be one of the modes listed below or a custom difficulty of the form
    "<number of mines>,<width>,<height>". If no difficulty is specified, then Terminal Mines will default to balanced.

    \b
    Terminal Mines difficulties:
    - balanced: A 20x15 board with 35 mines
    - challenging: A 25x20 board with 70 mines

    \b
    Official Minesweeper difficulties:
    - easy: A 8x8 board with 10 mines
    - intermediate: A 16x16 board with 40 mines
    - expert: A 16x30 board with 99 mines

    Note that this version of Minesweeper does not guarantee that your first move will always be safe. Additionally, in
    this version a "win" is defined as flagging all mines, not revealing all safe cells.

    The mines file (if provided) is used to control the placement of mines. It must be a CSV where each line is of the
    form "<x>,<y>". Both coordinates are 0-based and count from the top-left corner of the game board. If any of the
    specified mines are outside the bounds of the game board they will be skipped. If a mines file is provided the
    "number of mines" portion of the difficulty setting will be ignored.
    """
    minefield = random_minefield(*difficulty)
    key_handler = KeyHandler(minefield, ctx)
    render(minefield)
    input_loop(key_handler.handle_key)


if __name__ == "__main__":
    main()
