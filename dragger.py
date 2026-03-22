import pygame

from const import *


class Drager:
    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mousex = 0
        self.mousey = 0
        self.initial_row = 0
        self.initial_col = 0

    def update_blit(self, surface):
        self.piece.set_texture(size=128)
        img = pygame.image.load(self.piece.texture)
        img_center = (self.mousex, self.mousey)
        self.piece.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, pos):
        self.mousex, self.mousey = pos

    def save_initiial(self, pos):
        self.initial_row = pos[1] // SQUSIZE
        self.initial_col = pos[0] // SQUSIZE

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False
