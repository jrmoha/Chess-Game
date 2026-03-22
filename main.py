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
        self.menu_open = True
        self.menu_mode = "pvp"
        self.menu_difficulty = "medium"

    def draw_menu(self):
        screen = self.screen

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(150, 155, 500, 465)
        pygame.draw.rect(screen, (28, 28, 40), panel_rect, border_radius=14)
        pygame.draw.rect(screen, (75, 75, 105), panel_rect, width=2, border_radius=14)

        title_font = pygame.font.SysFont("monospace", 50, bold=True)
        btn_font = pygame.font.SysFont("monospace", 19, bold=True)
        label_font = pygame.font.SysFont("monospace", 15)

        title = title_font.render("CHESS", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 178))

        # Mode section
        mode_label = label_font.render("GAME MODE", True, (160, 160, 190))
        screen.blit(mode_label, (WIDTH // 2 - mode_label.get_width() // 2, 248))

        modes = [("pvp", "PvP"), ("r", "Random AI"), ("smart", "Stockfish")]
        mode_rects = {}
        btn_w, btn_h = 140, 44
        gap = 15
        total_w = len(modes) * btn_w + (len(modes) - 1) * gap
        start_x = WIDTH // 2 - total_w // 2
        btn_y = 272

        for i, (mode_key, mode_name) in enumerate(modes):
            rect = pygame.Rect(start_x + i * (btn_w + gap), btn_y, btn_w, btn_h)
            mode_rects[mode_key] = rect
            selected = self.menu_mode == mode_key
            bg_color = (65, 120, 175) if selected else (55, 55, 72)
            border_color = (115, 175, 255) if selected else (85, 85, 110)
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
            lbl = btn_font.render(mode_name, True, (255, 255, 255))
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

        # Difficulty section
        diff_active = self.menu_mode == "smart"
        diff_label_color = (160, 160, 190) if diff_active else (70, 70, 90)
        diff_label = label_font.render("DIFFICULTY", True, diff_label_color)
        screen.blit(diff_label, (WIDTH // 2 - diff_label.get_width() // 2, 348))

        diffs = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]
        diff_rects = {}
        total_w2 = len(diffs) * btn_w + (len(diffs) - 1) * gap
        start_x2 = WIDTH // 2 - total_w2 // 2
        dbtn_y = 372

        for i, (diff_key, diff_name) in enumerate(diffs):
            rect = pygame.Rect(start_x2 + i * (btn_w + gap), dbtn_y, btn_w, btn_h)
            diff_rects[diff_key] = rect
            if diff_active:
                selected = self.menu_difficulty == diff_key
                bg_color = (65, 120, 175) if selected else (55, 55, 72)
                border_color = (115, 175, 255) if selected else (85, 85, 110)
                text_color = (255, 255, 255)
            else:
                bg_color = (38, 38, 50)
                border_color = (55, 55, 68)
                text_color = (70, 70, 90)
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
            lbl = btn_font.render(diff_name, True, text_color)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

        # Play button
        play_rect = pygame.Rect(WIDTH // 2 - 95, 455, 190, 54)
        pygame.draw.rect(screen, (45, 155, 75), play_rect, border_radius=10)
        pygame.draw.rect(screen, (75, 210, 115), play_rect, width=2, border_radius=10)
        play_font = pygame.font.SysFont("monospace", 22, bold=True)
        play_lbl = play_font.render("PLAY", True, (255, 255, 255))
        screen.blit(play_lbl, (play_rect.centerx - play_lbl.get_width() // 2, play_rect.centery - play_lbl.get_height() // 2))

        hint = label_font.render("Press ESC during game to return here", True, (85, 85, 110))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 528))

        return mode_rects, diff_rects, play_rect

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

            if self.menu_open:
                mode_rects, diff_rects, play_rect = self.draw_menu()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.smart_ai.cleanup()
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        for mode_key, rect in mode_rects.items():
                            if rect.collidepoint(pos):
                                self.menu_mode = mode_key
                        for diff_key, rect in diff_rects.items():
                            if rect.collidepoint(pos) and self.menu_mode == "smart":
                                self.menu_difficulty = diff_key
                        if play_rect.collidepoint(pos):
                            self.menu_open = False
                            game.reset()
                            self.smart_ai.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                            game.mode = self.menu_mode
                            mode = self.menu_mode
                            self.difficulty = self.menu_difficulty

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.menu_open = False

            else:
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
                        if event.key == pygame.K_ESCAPE:
                            self.menu_open = True
                            self.menu_mode = mode
                            self.menu_difficulty = self.difficulty

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
