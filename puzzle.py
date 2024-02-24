from random import randint, shuffle
import pygame as pg
import prepare
from puzzle_piece import PuzzlePiece, PuzzleSection


class Puzzle(object):
    def __init__(self, puzzle_image):
        self.make_pieces(puzzle_image)
        self.piece_total = len(self.pieces)
        self.spread_pieces()
        self.sections = []

    def draw(self, surface):
        for section in reversed(self.sections):
            section.draw(surface)
        for piece in reversed(self.pieces.values()):
            piece.draw(surface)

    def make_pieces(self, puzzle_image):
        self.pieces = {}
        img = puzzle_image
        img_rect:pg.Rect = img.get_rect()
        pieceW = img_rect.w // 32 * 4
        pieceH = img_rect.h // 32 * 4
        for column in range(0, 8):
            x = column * pieceW
            for row in range(0, 8):
                y = row * pieceH
                rect = pg.Rect(x - img_rect.h // 32, y - img_rect.h // 32,
                               3 * img_rect.w // 16, 3 * img_rect.h // 16)
                clipped = rect.clip(img_rect)
                offset = clipped.x - rect.x, clipped.y - rect.y
                surf = pg.Surface((3 * img_rect.w // 16, 3 * img_rect.h // 16))
                surf.blit(img.subsurface(clipped), offset)
                cover:pg.Surface = prepare.GFX[f"piece{column}-{row}"]
                cover = pg.transform.scale(cover, [3 * img_rect.w // 16, 3 * img_rect.h // 16])
                surf.blit(cover, (0, 0))
                surf.set_colorkey(pg.Color("black"))
                self.pieces[(column, row)] = PuzzlePiece((column, row), surf, (x, y), (pieceW, pieceH))
        for piece in self.pieces.values():
            piece.get_neighbors(self.pieces)
        
    def spread_pieces(self):
        screen_w, screen_h  = prepare.SCREEN_SIZE
        w = screen_w // 8
        h = screen_h // 8
        rects = [pg.Rect(x, y, w, h)
                for x in range(0, w*8-1, w)
                for y in range(0, h*8-1, h)]
        pieces = list(self.pieces.values())
        for piece in pieces:
            turns = randint(0,3)
            piece.rotate(90 * turns)
        shuffle(pieces)
        for p, rect in zip(pieces, rects):
            p.rect.center = rect.center
            
    def join_pieces(self, piece1:PuzzlePiece, piece2:PuzzlePiece):
        p1 = pg.Rect((0, 0), piece1.size)
        p2 = p1.copy()
        p1.center = piece1.rect.center
        for side in piece2.neighbors:
            rotatedSide = piece2.getRotatedSide(side)
            if piece1 is piece2.neighbors[side]:
                if rotatedSide == "left":
                    p2.left = p1.right
                    p2.top = p1.top
                elif rotatedSide == "right":
                    p2.right = p1.left
                    p2.top = p1.top
                elif rotatedSide == "top":
                    p2.top = p1.bottom
                    p2.left = p1.left
                elif rotatedSide == "bottom":
                    p2.bottom = p1.top
                    p2.left = p1.left
        piece2.rect.center = p2.center
        section = PuzzleSection((piece1, piece2))
        indices = (piece1.index, piece2.index)
        for ind in indices:
            try:
                del self.pieces[ind]
            except KeyError:
                pass
        self.sections.append(section)
        
        





            
            
