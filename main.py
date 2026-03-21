import pygame
import sys

from const import *
from game import *
from piece import *
from board import *
from square import *
from smart_ai import SmartAI


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        pygame_icon = pygame.image.load("chess.png")
        pygame.display.set_icon(pygame_icon)
        self.game = Game()
        self.smart_ai = SmartAI()
        self.difficulty = "medium"

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        mode = self.game.mode

        while True:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            game.show_hud(screen, mode, self.difficulty)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                if mode == "pvp":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)
                        clicked_row = dragger.mousey // SQUSIZE
                        clicked_col = dragger.mousex // SQUSIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initiial(event.pos)
                                dragger.drag_piece(piece)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)

                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQUSIZE
                        motion_col = event.pos[0] // SQUSIZE
                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            released_row = dragger.mousey // SQUSIZE
                            released_col = dragger.mousex // SQUSIZE

                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)
                                game.play_sound(captured)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                game.next_turn()

                        dragger.undrag_piece()

                elif mode == "r":
                    if game.next_player == "white":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            dragger.update_mouse(event.pos)
                            clicked_row = dragger.mousey // SQUSIZE
                            clicked_col = dragger.mousex // SQUSIZE

                            if board.squares[clicked_row][clicked_col].has_piece():
                                piece = board.squares[clicked_row][clicked_col].piece
                                if piece.color == game.next_player:
                                    board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                    dragger.save_initiial(event.pos)
                                    dragger.drag_piece(piece)
                                    game.show_bg(screen)
                                    game.show_last_move(screen)
                                    game.show_moves(screen)
                                    game.show_pieces(screen)

                        elif event.type == pygame.MOUSEMOTION:
                            motion_row = event.pos[1] // SQUSIZE
                            motion_col = event.pos[0] // SQUSIZE
                            game.set_hover(motion_row, motion_col)

                            if dragger.dragging:
                                dragger.update_mouse(event.pos)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                                game.show_hover(screen)
                                dragger.update_blit(screen)

                        elif event.type == pygame.MOUSEBUTTONUP:
                            if dragger.dragging:
                                dragger.update_mouse(event.pos)
                                released_row = dragger.mousey // SQUSIZE
                                released_col = dragger.mousex // SQUSIZE

                                initial = Square(dragger.initial_row, dragger.initial_col)
                                final = Square(released_row, released_col)
                                move = Move(initial, final)

                                if board.valid_move(dragger.piece, move):
                                    captured = board.squares[released_row][released_col].has_piece()
                                    board.move(dragger.piece, move)
                                    board.set_true_en_passant(dragger.piece)
                                    game.play_sound(captured)
                                    game.show_bg(screen)
                                    game.show_last_move(screen)
                                    game.show_pieces(screen)
                                    game.next_turn()

                            dragger.undrag_piece()

                    elif game.next_player == "black":
                        piece, move = game.get_random_move()

                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)

                        if move is None:
                            game.show_win_msg(screen, "white")
                            pygame.display.update()
                            pygame.time.delay(3000)
                            game.reset()
                            game.mode = "r"
                            mode = "r"
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                        elif board.valid_move(piece, move):
                            captured = board.squares[move.final.row][move.final.col].has_piece()
                            board.move(piece, move)
                            board.set_true_en_passant(piece)
                            game.play_sound(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.next_turn()

                elif mode == "smart":
                    if game.next_player == "white":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            dragger.update_mouse(event.pos)
                            clicked_row = dragger.mousey // SQUSIZE
                            clicked_col = dragger.mousex // SQUSIZE

                            if board.squares[clicked_row][clicked_col].has_piece():
                                piece = board.squares[clicked_row][clicked_col].piece
                                if piece.color == game.next_player:
                                    board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                    dragger.save_initiial(event.pos)
                                    dragger.drag_piece(piece)
                                    game.show_bg(screen)
                                    game.show_last_move(screen)
                                    game.show_moves(screen)
                                    game.show_pieces(screen)

                        elif event.type == pygame.MOUSEMOTION:
                            motion_row = event.pos[1] // SQUSIZE
                            motion_col = event.pos[0] // SQUSIZE
                            game.set_hover(motion_row, motion_col)

                            if dragger.dragging:
                                dragger.update_mouse(event.pos)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                                game.show_hover(screen)
                                dragger.update_blit(screen)

                        elif event.type == pygame.MOUSEBUTTONUP:
                            if dragger.dragging:
                                dragger.update_mouse(event.pos)
                                released_row = dragger.mousey // SQUSIZE
                                released_col = dragger.mousex // SQUSIZE

                                initial = Square(dragger.initial_row, dragger.initial_col)
                                final = Square(released_row, released_col)
                                move = Move(initial, final)

                                if board.valid_move(dragger.piece, move):
                                    captured = board.squares[released_row][released_col].has_piece()
                                    moved_piece = dragger.piece
                                    board.move(dragger.piece, move)
                                    board.set_true_en_passant(moved_piece)
                                    is_promotion = isinstance(moved_piece, Pawn) and released_row == 0
                                    self.smart_ai.push_move(
                                        dragger.initial_row, dragger.initial_col,
                                        released_row, released_col,
                                        "q" if is_promotion else None,
                                    )
                                    game.play_sound(captured)
                                    game.show_bg(screen)
                                    game.show_last_move(screen)
                                    game.show_pieces(screen)
                                    game.next_turn()

                            dragger.undrag_piece()

                    elif game.next_player == "black":
                        result = self.smart_ai.get_move(self.difficulty)

                        if result is not None:
                            from_row, from_col, to_row, to_col, promotion = result
                            piece = board.squares[from_row][from_col].piece
                            board.calc_moves(piece, from_row, from_col, bool=True)
                            move = Move(Square(from_row, from_col), Square(to_row, to_col))
                        else:
                            piece, move = game.get_random_move()
                            from_row = from_col = to_row = to_col = promotion = None
                            if move is not None:
                                from_row, from_col = move.initial.row, move.initial.col
                                to_row, to_col = move.final.row, move.final.col

                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)

                        if move is None:
                            game.show_win_msg(screen, "white")
                            pygame.display.update()
                            pygame.time.delay(3000)
                            game.reset()
                            self.smart_ai.reset()
                            game.mode = "smart"
                            mode = "smart"
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                        elif board.valid_move(piece, move):
                            captured = board.squares[move.final.row][move.final.col].has_piece()
                            board.move(piece, move)
                            board.set_true_en_passant(piece)
                            self.smart_ai.push_move(
                                move.initial.row, move.initial.col,
                                move.final.row, move.final.col,
                                promotion,
                            )
                            game.play_sound(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.next_turn()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        game.change_theme()

                    if event.key == pygame.K_r:
                        game.reset()
                        self.smart_ai.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                    if event.key == pygame.K_p:
                        game.reset()
                        game.mode = "pvp"
                        mode = "pvp"
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                    if event.key == pygame.K_h:
                        game.reset()
                        game.mode = "r"
                        mode = "r"
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                    if event.key == pygame.K_s:
                        game.reset()
                        self.smart_ai.reset()
                        game.mode = "smart"
                        mode = "smart"
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                    if mode == "smart":
                        if event.key == pygame.K_1:
                            self.difficulty = "easy"
                        elif event.key == pygame.K_2:
                            self.difficulty = "medium"
                        elif event.key == pygame.K_3:
                            self.difficulty = "hard"

                if event.type == pygame.QUIT:
                    self.smart_ai.cleanup()
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    main.mainloop()
