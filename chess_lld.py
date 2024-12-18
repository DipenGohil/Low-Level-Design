# -*- coding: utf-8 -*-
"""Chess_LLD.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vd3xg5mm9zLWALpkKThccv0qd8lCy0Wq
"""

from abc import ABC, abstractmethod
from typing import List, Optional

# Constants for chess
BOARD_SIZE = 8

# Enum for piece color
class Color:
    WHITE = "White"
    BLACK = "Black"

# Abstract class for a ChessPiece
class ChessPiece(ABC):
    def __init__(self, color: str):
        self.color = color

    @abstractmethod
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        pass

# Specific piece implementations
class Pawn(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        direction = 1 if self.color == Color.WHITE else -1

        if start_col == end_col:  # Forward move
            if board.get_piece(end) is None:
                if (end_row - start_row) == direction:
                    return True
                if (end_row - start_row) == 2 * direction and (start_row == 1 or start_row == 6):
                    return board.get_piece((start_row + direction, start_col)) is None

        elif abs(end_col - start_col) == 1 and (end_row - start_row) == direction:  # Capture
            if board.get_piece(end) and board.get_piece(end).color != self.color:
                return True

        return False

class Rook(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        start_row, start_col = start
        end_row, end_col = end

        if start_row == end_row or start_col == end_col:
            step_row = (end_row - start_row) // max(1, abs(end_row - start_row))
            step_col = (end_col - start_col) // max(1, abs(end_col - start_col))
            current = (start_row + step_row, start_col + step_col)
            while current != end:
                if board.get_piece(current) is not None:
                    return False
                current = (current[0] + step_row, current[1] + step_col)
            return board.get_piece(end) is None or board.get_piece(end).color != self.color

        return False

class Knight(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        start_row, start_col = start
        end_row, end_col = end

        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)

        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            return board.get_piece(end) is None or board.get_piece(end).color != self.color

        return False

class Bishop(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        start_row, start_col = start
        end_row, end_col = end

        if abs(start_row - end_row) == abs(start_col - end_col):
            step_row = (end_row - start_row) // abs(end_row - start_row)
            step_col = (end_col - start_col) // abs(end_col - start_col)
            current = (start_row + step_row, start_col + step_col)
            while current != end:
                if board.get_piece(current) is not None:
                    return False
                current = (current[0] + step_row, current[1] + step_col)
            return board.get_piece(end) is None or board.get_piece(end).color != self.color

        return False

class Queen(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        rook = Rook(self.color)
        bishop = Bishop(self.color)
        return rook.is_valid_move(start, end, board) or bishop.is_valid_move(start, end, board)

class King(ChessPiece):
    def is_valid_move(self, start: tuple, end: tuple, board) -> bool:
        start_row, start_col = start
        end_row, end_col = end

        if max(abs(start_row - end_row), abs(start_col - end_col)) == 1:
            return board.get_piece(end) is None or board.get_piece(end).color != self.color

        return False

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def place_piece(self, piece: ChessPiece, position: tuple):
        self.grid[position[0]][position[1]] = piece

    def get_piece(self, position: tuple) -> Optional[ChessPiece]:
        return self.grid[position[0]][position[1]]

    def move_piece(self, start: tuple, end: tuple) -> bool:
        piece = self.get_piece(start)
        if piece and piece.is_valid_move(start, end, self):
            self.grid[end[0]][end[1]] = piece
            self.grid[start[0]][start[1]] = None
            return True
        return False

class Player:
    def __init__(self, color: str):
        self.color = color

class Game:
    def __init__(self):
        self.board = Board()
        self.players = [Player(Color.WHITE), Player(Color.BLACK)]
        self.current_turn = 0

    def initialize_pieces(self):
        # Set up pawns
        for col in range(BOARD_SIZE):
            self.board.place_piece(Pawn(Color.WHITE), (1, col))
            self.board.place_piece(Pawn(Color.BLACK), (6, col))

        # Set up rooks
        self.board.place_piece(Rook(Color.WHITE), (0, 0))
        self.board.place_piece(Rook(Color.WHITE), (0, 7))
        self.board.place_piece(Rook(Color.BLACK), (7, 0))
        self.board.place_piece(Rook(Color.BLACK), (7, 7))

        # Set up knights
        self.board.place_piece(Knight(Color.WHITE), (0, 1))
        self.board.place_piece(Knight(Color.WHITE), (0, 6))
        self.board.place_piece(Knight(Color.BLACK), (7, 1))
        self.board.place_piece(Knight(Color.BLACK), (7, 6))

        # Set up bishops
        self.board.place_piece(Bishop(Color.WHITE), (0, 2))
        self.board.place_piece(Bishop(Color.WHITE), (0, 5))
        self.board.place_piece(Bishop(Color.BLACK), (7, 2))
        self.board.place_piece(Bishop(Color.BLACK), (7, 5))

        # Set up queens
        self.board.place_piece(Queen(Color.WHITE), (0, 3))
        self.board.place_piece(Queen(Color.BLACK), (7, 3))

        # Set up kings
        self.board.place_piece(King(Color.WHITE), (0, 4))
        self.board.place_piece(King(Color.BLACK), (7, 4))

    def play_turn(self, start: tuple, end: tuple) -> bool:
        current_player = self.players[self.current_turn % 2]
        piece = self.board.get_piece(start)

        if piece is None:
            print("No piece at the start position.")
            return False

        if piece.color != current_player.color:
            print("It's not your turn.")
            return False

        if self.board.move_piece(start, end):
            self.current_turn += 1
            return True

        print("Invalid move.")
        return False

# Future extension: Add AIPlayer that extends Player
class AIPlayer(Player):
    def make_move(self, board: Board):
        pass  # Implement AI move logic

# Example Usage
game = Game()
game.initialize_pieces()

# Example moves
print(game.play_turn((1, 0), (3, 0)))  # White pawn moves forward two spaces
print(game.play_turn((6, 0), (4, 0)))  # Black pawn moves forward two spaces
print(game.play_turn((3, 0), (4, 0)))  # Invalid move