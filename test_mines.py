import unittest
from enum import Enum
from unittest.mock import MagicMock, patch

from mines import DIFFICULTY_PRESETS, DifficultyParamType, KeyHandler
from mines import main as main_function


# import click

class MinesTestCase(unittest.TestCase):
    def test_difficulty_param_type(self):
        difficulty_param_type_obj = DifficultyParamType()
        DIFFICULTY_PRESETS = {
            "balanced": (35, 20, 15),
            "challenging": (70, 25, 20),
            "easy": (10, 8, 8),
            "intermediate": (40, 16, 16),
            "expert": (99, 16, 30)
        }
        self.assertEqual(difficulty_param_type_obj.convert("balanced", None, None), DIFFICULTY_PRESETS["balanced"])
        self.assertEqual(difficulty_param_type_obj.convert("challenging", None, None),
                         DIFFICULTY_PRESETS["challenging"])
        self.assertEqual(difficulty_param_type_obj.convert("easy", None, None), DIFFICULTY_PRESETS["easy"])
        self.assertEqual(difficulty_param_type_obj.convert("intermediate", None, None),
                         DIFFICULTY_PRESETS["intermediate"])
        self.assertEqual(difficulty_param_type_obj.convert("expert", None, None), DIFFICULTY_PRESETS["expert"])

    def test_difficulty_param_type_custom_difficulty(self):
        difficulty_param_type_obj = DifficultyParamType()
        self.assertEqual(difficulty_param_type_obj.convert("50, 10,10", None, None), (50, 10, 10))

    def test_difficulty_param_type_invalid_difficulty_name(self):
        difficulty_param_type_obj = DifficultyParamType()
        from click import BadParameter
        self.assertRaises(BadParameter, difficulty_param_type_obj.convert, "invalid", None, None)

    def test_difficulty_param_type_invalid_difficulty_name_2(self):
        difficulty_param_type_obj = DifficultyParamType()
        from click import BadParameter
        self.assertRaises(BadParameter, difficulty_param_type_obj.convert, "10,10", None, None)

    def test_difficulty_param_type_invalid_difficulty_name_3(self):
        difficulty_param_type_obj = DifficultyParamType()
        from click import BadParameter
        self.assertRaises(BadParameter, difficulty_param_type_obj.convert, "-1, 10,10", None, None)

    def test_difficulty_param_type_invalid_difficulty_name_4(self):
        difficulty_param_type_obj = DifficultyParamType()
        from click import BadParameter
        self.assertRaises(BadParameter, difficulty_param_type_obj.convert, "5, 55,10", None, None)

    def test_difficulty_param_type_invalid_difficulty_name_5(self):
        difficulty_param_type_obj = DifficultyParamType()
        from click import BadParameter
        self.assertRaises(BadParameter, difficulty_param_type_obj.convert, "101, 10,10", None, None)


class Renderer(unittest.TestCase):
    # INTEGRATION TEST 1 minefield, cell and render_cell
    def test_render_cell_integration_minefield_normal_cell(self):
        from game_logic.renderer import render_cell
        from game_logic import random_minefield
        from game_logic.game_model import GameState, CellState
        from click import style
        fg_mapping = {
            CellState.FLAGGED: "bright_green",
            CellState.WARN1: "bright_cyan",
            CellState.WARN2: "cyan",
            CellState.WARN3: "bright_blue",
            CellState.WARN4: "bright_magenta",
            CellState.WARN5: "magenta",
            CellState.WARN6: "bright_yellow",
            CellState.WARN7: "red",
            CellState.WARN8: "red",
            CellState.EXPLODED: "bright_red"
        }

        minefield = random_minefield(35, 20, 15)
        minefield.x = 1
        minefield.y = 0
        cell = minefield.get_cell(0, 0)
        bg = None
        fg = fg_mapping.get(cell.state, None)

        self.assertEqual(render_cell(minefield, 0, 0), style(cell.state.value, bg=bg, fg=fg))

    def test_render_cell_integration_minefield_inprogress_game_current_cell(self):
        from game_logic.renderer import render_cell
        from game_logic import random_minefield
        from game_logic.game_model import GameState
        from click import style

        minefield = random_minefield(35, 20, 15)
        minefield.x = 0
        minefield.y = 0

        cell = minefield.get_cell(0, 0)

        minefield.state = GameState.IN_PROGRESS
        bg = "bright_green"
        fg = "black"

        self.assertEqual(render_cell(minefield, 0, 0), style(cell.state.value, bg=bg, fg=fg))

    def test_render_cell_integration_minefield_finished_game_flagged_cell(self):
        from game_logic.renderer import render_cell
        from game_logic import random_minefield
        from game_logic.game_model import GameState, CellState
        from click import style
        fg_mapping = {
            CellState.FLAGGED: "bright_green",
            CellState.WARN1: "bright_cyan",
            CellState.WARN2: "cyan",
            CellState.WARN3: "bright_blue",
            CellState.WARN4: "bright_magenta",
            CellState.WARN5: "magenta",
            CellState.WARN6: "bright_yellow",
            CellState.WARN7: "red",
            CellState.WARN8: "red",
            CellState.EXPLODED: "bright_red"
        }

        minefield = random_minefield(35, 20, 15)

        minefield.flag_cell(0, 0)
        cell = minefield.get_cell(0, 0)
        cell.is_mine = False
        minefield.state = GameState.WON
        bg = "red"
        fg = fg_mapping.get(cell.state, None)
        self.assertEqual(render_cell(minefield, 0, 0), style(cell.state.value, bg=bg, fg=fg))

    # INTEGRATION TEST 2 minefield and gen_lines
    def test_gen_lines(self):
        from game_logic.renderer import render, gen_lines
        from game_logic import random_minefield
        minefield = random_minefield(2, 3, 3)
        out_put = "┌───────┐\n│ [30m[102m?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n└───────┘\n Flags remaining: 2"
        # print("\n".join(gen_lines(minefield)))
        self.assertEqual("\n".join(gen_lines(minefield)), out_put)

    def test_gen_lines_lose_game(self):
        from game_logic.renderer import render, gen_lines
        from game_logic import random_minefield
        from game_logic.game_model import GameState
        minefield = random_minefield(2, 3, 3)
        minefield.state = GameState.LOST
        out_put = "┌───────┐\n│ ?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n└───────┘\n Game lost"
        # print("\n".join(gen_lines(minefield)))
        self.assertEqual("\n".join(gen_lines(minefield)), out_put)

    def test_gen_lines_win_game(self):
        from game_logic.renderer import render, gen_lines
        from game_logic import random_minefield
        from game_logic.game_model import GameState
        minefield = random_minefield(2, 3, 3)
        minefield.state = GameState.WON
        out_put = "┌───────┐\n│ ?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n│ ?[0m ?[0m ?[0m │\n└───────┘\n Game won"
        # print("\n".join(gen_lines(minefield)))
        self.assertEqual("\n".join(gen_lines(minefield)), out_put)


class KeyboardListenerTest(unittest.TestCase):

    @patch('builtins.print')
    def test_demo_handler(self, mock_print):
        from game_logic.keyboard_listener import demo_handler
        demo_handler('test')
        mock_print.assert_called_with("Processing 'test'")

    def test_translate_key_letter_move(self):
        from game_logic.keyboard_listener import translate_key
        self.assertEqual(translate_key("A"), "a")
        self.assertEqual(translate_key("a"), "a")

    def test_translate_key_escape_reveal_move(self):
        from game_logic.keyboard_listener import translate_key
        self.assertEqual(translate_key("\r"), "\n")
        self.assertEqual(translate_key("\x1b"), None)

    def test_translate_key_arrow_move(self):
        from game_logic.keyboard_listener import translate_key
        self.assertEqual(translate_key("àH"), "w")
        self.assertEqual(translate_key("àP"), "s")
        self.assertEqual(translate_key("àK"), "a")
        self.assertEqual(translate_key("àM"), "d")

    # INTEGRATION TEST 5 minefield and key_handler
    @patch('mines.render')
    def test_handler_move_left(self, mock_render):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        mock_ctx = MagicMock()
        mock_render.return_value = 0
        minefield.x = 10
        minefield.y = 10
        coordinates = (minefield.x, minefield.y)
        key_handler = KeyHandler(minefield, mock_ctx)
        key_handler.handle_key("a")
        self.assertEqual((minefield.x, minefield.y), (coordinates[0] - 1, coordinates[1]))

    @patch('mines.render')
    def test_handler_move_right(self, mock_render):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        mock_ctx = MagicMock()
        mock_render.return_value = 0
        minefield.x = 10
        minefield.y = 10
        coordinates = (minefield.x, minefield.y)
        key_handler = KeyHandler(minefield, mock_ctx)
        key_handler.handle_key("d")
        self.assertEqual((minefield.x, minefield.y), (coordinates[0] + 1, coordinates[1]))

    @patch('mines.render')
    def test_handler_move_up(self, mock_render):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        mock_ctx = MagicMock()
        mock_render.return_value = 0
        minefield.x = 10
        minefield.y = 10
        coordinates = (minefield.x, minefield.y)
        key_handler = KeyHandler(minefield, mock_ctx)
        key_handler.handle_key("w")
        self.assertEqual((minefield.x, minefield.y), (coordinates[0], coordinates[1] - 1))

    @patch('mines.render')
    def test_handler_move_down(self, mock_render):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        mock_ctx = MagicMock()
        mock_render.return_value = 0
        minefield.x = 10
        minefield.y = 10
        coordinates = (minefield.x, minefield.y)
        key_handler = KeyHandler(minefield, mock_ctx)
        key_handler.handle_key("s")
        self.assertEqual((minefield.x, minefield.y), (coordinates[0], coordinates[1] + 1))

    @patch('mines.render')
    def test_handler_flag_cell(self, mock_render):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        mock_ctx = MagicMock()
        mock_render.return_value = 0
        minefield.x = 10
        minefield.y = 10

        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        key_handler = KeyHandler(minefield, mock_ctx)
        key_handler.handle_key("e")
        cell = minefield.get_cell(minefield.x, minefield.y)
        self.assertEqual(cell.state.value, CellState.FLAGGED.value)


class CellTest(unittest.TestCase):
    def test__repr__(self):
        from game_logic.game_model import Cell
        cell = Cell(True)
        self.assertEqual(cell.__repr__(), "Cell(True, ?)")


class Minefield(unittest.TestCase):
    def test___repr__(self):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        self.assertEqual(minefield.__repr__(), "Minefield(20, 15)")

    def test_num_mines(self):
        from game_logic import random_minefield
        minefield = random_minefield(35, 20, 15)
        self.assertEqual(minefield.num_mines, 35)

    def test_cords_and_cells(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        cell = minefield.get_cell(0, 0)
        cell.is_mine = False
        cords_and_cell_0 = list(minefield.cords_and_cells)[0]
        self.assertEqual((cords_and_cell_0[0], cords_and_cell_0[0]), (0, 0))
        self.assertIsInstance(cords_and_cell_0[2], Cell)

    def test_get_cell_valid_index(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        cell = minefield.get_cell(0, 0)
        self.assertIsInstance(cell, Cell)

    def test_get_cell_invalid_index(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        self.assertRaises(IndexError, minefield.get_cell, 6, 0)

    # INTEGRATION TEST 3 minefield and cell to flag a cell
    def test_flag_cell(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        cell = minefield.get_cell(0, 0)

        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        # cell.state = CellState.FLAGGED
        minefield.flag_cell(0, 0)
        self.assertEqual(minefield.get_cell(0, 0).state.value, CellState.FLAGGED.value)

    def test_unflag_cell(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        cell = minefield.get_cell(0, 0)

        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        minefield.flag_cell(0, 0)
        minefield.flag_cell(0, 0)
        self.assertEqual(minefield.get_cell(0, 0).state.value, CellState.UNKNOWN.value)

    # INTEGRATION TEST 4 minefield and cell to reveal a cell
    def test_reveal_cell_safe_neighbours(self):
        from game_logic import random_minefield, Minefield
        from game_logic.game_model import Cell
        mines = set()
        mines.add("{},{}".format(4, 4))

        minefield = Minefield(5, 5, mines)
        ismine_mock = False
        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        minefield.reveal_cell(0, 0)
        # self.assertEqual(minefield.reveal_cell(0, 0), None)
        self.assertEqual(minefield.get_cell(0, 0).state.value, CellState.SAFE.value)

    def test_reveal_cell_mine_neighbours(self):
        from game_logic import random_minefield, Minefield
        from game_logic.game_model import Cell
        mines = set()
        mines.add("{},{}".format(0, 1))

        minefield = Minefield(5, 5, mines)
        ismine_mock = False
        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        minefield.reveal_cell(0, 0)
        # self.assertEqual(minefield.reveal_cell(0, 0), None)
        self.assertEqual(minefield.get_cell(0, 0).state.value, CellState.WARN1.value)

    def test_reveal_flagged_cell(self):
        from game_logic import random_minefield
        from game_logic.game_model import Cell
        minefield = random_minefield(5, 5, 5)
        minefield.flag_cell(0, 0)
        self.assertEqual(minefield.reveal_cell(0, 0), None)

    def test_reveal_mine_cell(self):
        from game_logic import random_minefield, Minefield
        from game_logic.game_model import Cell
        mines = set()
        mines.add("{},{}".format(0, 0))

        minefield = Minefield(5, 5, mines)

        class CellState(Enum):
            UNKNOWN = "?"
            SAFE = "-"
            WARN1 = "1"
            WARN2 = "2"
            WARN3 = "3"
            WARN4 = "4"
            WARN5 = "5"
            WARN6 = "6"
            WARN7 = "7"
            WARN8 = "8"
            FLAGGED = "F"
            EXPLODED = "X"

        # cell = minefield.get_cell(0, 0)
        # cell.is_mine = True
        minefield.reveal_cell(0, 0)
        # self.assertEqual(minefield.reveal_cell(0, 0), None)
        self.assertEqual(minefield.get_cell(0, 0).state.value, CellState.EXPLODED.value)
