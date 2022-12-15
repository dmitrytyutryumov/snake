import enum
import random
import sys
from copy import deepcopy

from pynput import keyboard

# install pynput !!!!!!!!!!


class GameOver(Exception):
    ...


@enum.unique
class Movements(enum.Enum):
    up = [-1, 0]
    down = [1, 0]
    left = [0, -1]
    right = [0, 1]


class PRINT_COLORS:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Snake:
    icon = "D"
    head_icon = "H"

    def __init__(self, start_position: int) -> None:
        self._body = [[start_position, start_position]]

    def get_body(self) -> list:
        return self._body

    def move(self, action: Movements) -> list:
        new_pos_x, new_pos_y = action.value

        head_x, head_y = self._body[0]
        head_x += new_pos_x
        head_y += new_pos_y

        if [head_x, head_y] in self._body[:-1]:
            raise_game_over()

        self._body = [[head_x, head_y], *self._body[:-1]]
        return self._body

    def eat(self):
        x, y = self._body[-1]
        self._body.append([x, y])
        return self._body


class Food:
    icon = "F"

    def __init__(self, board_size: list) -> None:
        self._range = range(board_size)
        self._position = []

    def draw(self, snake_body: list) -> list:
        self._position = self._generate_position(snake_body)
        return self._position

    def _generate_position(self, snake_body: list) -> list:
        position = [
            random.choice([i for i in self._range]),
            random.choice([i for i in self._range]),
        ]

        if position in snake_body:
            self._generate_position(snake_body)
        return position

    def get_position(self) -> list:
        return self._position


class Board:
    def __init__(self, size: int = 10, snake: "Snake" = None) -> None:
        self._size = size
        self._snake = snake
        self._board = self._draw_init_board()

    def get_size(self) -> int:
        return self._size

    def draw(self, snake_body: list, food: list) -> list:
        new_board = deepcopy(self._board)
        self.draw_snake(snake_body, new_board)
        self.draw_food(food, new_board)

        print("\033c")
        for row in new_board:
            print(PRINT_COLORS.OKBLUE + str(row) + PRINT_COLORS.ENDC, end="\n")

    def draw_food(self, food: list, new_board: list) -> list:
        new_board[food[0]][food[1]] = Food.icon
        return new_board

    def draw_snake(self, snake_body: list, new_board: list) -> list:
        for idx, (pos_x, pos_y) in enumerate(snake_body):
            if pos_x < 0 or pos_x >= self._size or pos_y < 0 or pos_y >= self._size:
                raise_game_over()

            new_board[pos_x][pos_y] = Snake.icon if idx > 0 else Snake.head_icon
        return new_board

    def _draw_init_board(self):
        _board = []
        for i in range(self._size):
            _board.append([" " for j in range(self._size)])

        return _board


def add_listeners(board: Board, snake: Snake, food: Food):
    def on_release(key):
        if key == keyboard.Key.left:
            move(board, snake, food, Movements.left)
        elif key == keyboard.Key.right:
            move(board, snake, food, Movements.right)
        elif key == keyboard.Key.up:
            move(board, snake, food, Movements.up)
        elif key == keyboard.Key.down:
            move(board, snake, food, Movements.down)

        if key == keyboard.Key.esc:
            # Stop listener
            return False

    with keyboard.Listener(on_release=on_release) as listener:
        listener.join()


def move(board: Board, snake: Snake, food: Food, action: Movements) -> None:
    snake_body = snake.move(action)
    if snake_body[0] == food.get_position():
        snake_body = snake.eat()
        food.draw(snake_body)

    board.draw(snake_body, food.get_position())


def raise_game_over():
    print(PRINT_COLORS.FAIL + "Game Over" + PRINT_COLORS.ENDC)
    sys.exit()


def main():
    board_size = int(input("Type board size: ") or 5)
    board = Board(board_size)

    start_position = round(board.get_size() / 2)
    snake = Snake(start_position)
    snake_body = snake.get_body()

    food = Food(board_size)

    board.draw(snake_body, food.draw(snake_body))

    add_listeners(board, snake, food)


if __name__ == "__main__":
    main()
