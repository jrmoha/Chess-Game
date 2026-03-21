import random
import pygame

from const import *
from board import *
from dragger import Drager
from piece import *
from move import *
from config import *
from square import *


class Game:
    def __init__(self):
        self.next_player = "white"
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Drager()
        self.config = Config()
        self.mode = "pvp"
        self.gameOver = False

    def show_bg(self, surface):
        theme = self.config.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                rect = (col * SQUSIZE, row * SQUSIZE, SQUSIZE, SQUSIZE)
                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS - row), 1, color)
                    lbl_pos = (5, 5 + row * SQUSIZE)
                    surface.blit(lbl, lbl_pos)

                    if row == 7:
                        color = (
                            theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                        )
                        lbl = self.config.font.render(
                            Square.get_alphacol(col), 1, color
                        )
                        lbl_pos = (col * SQUSIZE + SQUSIZE - 20, HEIGHT - 20)
                        surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = (
                            col * SQUSIZE + SQUSIZE // 2,
                            row * SQUSIZE + SQUSIZE // 2,
                        )
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme
        if self.dragger.dragging:
            piece = self.dragger.piece
            for move in piece.moves:
                color = (
                    theme.moves.light
                    if (move.final.row + move.final.col) % 2 == 0
                    else theme.moves.dark
                )
                rect = (
                    move.final.col * SQUSIZE,
                    move.final.row * SQUSIZE,
                    SQUSIZE,
                    SQUSIZE,
                )
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = (
                    theme.trace.light
                    if (pos.row + pos.col) % 2 == 0
                    else theme.trace.dark
                )
                rect = (pos.col * SQUSIZE, pos.row * SQUSIZE, SQUSIZE, SQUSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (
                self.hovered_sqr.col * SQUSIZE,
                self.hovered_sqr.row * SQUSIZE,
                SQUSIZE,
                SQUSIZE,
            )
            pygame.draw.rect(surface, color, rect, width=3)

    def show_hud(self, surface, mode, difficulty=None):
        mode_names = {"pvp": "PvP", "r": "Random AI", "smart": "Stockfish"}
        mode_text = mode_names.get(mode, mode)
        if mode == "smart" and difficulty:
            text = f"{mode_text}  {difficulty.capitalize()}  [1/2/3]"
        else:
            text = mode_text

        lbl = self.config.font.render(text, True, (255, 255, 255))
        w, h = lbl.get_size()
        x = WIDTH - w - 8
        y = 6
        bg = pygame.Surface((w + 10, h + 6))
        bg.set_alpha(160)
        bg.fill((0, 0, 0))
        surface.blit(bg, (x - 5, y - 3))
        surface.blit(lbl, (x, y))

    def next_turn(self):
        self.next_player = "white" if self.next_player == "black" else "black"

    def get_random_piece(self):
        pieces = self.board.get_peaces(self.next_player)
        return random.choice(list(pieces.items()))

    def get_random_move(self):
        piece, pos = self.get_random_piece()
        self.board.calc_moves(piece, pos[0], pos[1], bool=True)
        i = 0

        while piece.moves == [] and i < 100:
            piece, pos = self.get_random_piece()
            self.board.calc_moves(piece, pos[0], pos[1], bool=True)
            i += 1

        try:
            move = random.choice(piece.moves)
        except Exception:
            return piece, None

        if not self.board.in_check(piece, move):
            return piece, move

        return piece, None

    def show_win_msg(self, surface, winner):
        lbl = self.config.font.render(f"{winner} won!", 1, (255, 255, 255))
        lbl_pos = (
            WIDTH // 2 - lbl.get_width() // 2,
            HEIGHT // 2 - lbl.get_height() // 2,
        )
        rect = (0, HEIGHT // 2 - lbl.get_height() // 2, WIDTH, lbl.get_height())
        pygame.draw.rect(surface, (0, 0, 0), rect)
        surface.blit(lbl, lbl_pos)

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
