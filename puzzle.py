from random import randint, shuffle
import pygame as pg
import prepare
from puzzle_piece import PuzzlePiece, PuzzleSection, HexPuzzlePiece, HexPuzzleSection
from math import sqrt, ceil, sin, cos, pi

class Puzzle(object):
    def __init__(self, puzzle_image:pg.Surface):
        self.sections:list[PuzzleSection] = []
        self.make_pieces(puzzle_image)
        self.spread_pieces()

    def draw(self, surface:pg.Surface):
        for section in reversed(self.sections):
            section.draw(surface)
        for piece in reversed(self.pieces.values()):
            piece.draw(surface)
    
    def set_image(self, puzzle_image:pg.Surface):
        img:pg.Surface = puzzle_image
        img = img.convert(24)
        scalar = 800 / max(img.get_size())
        img = pg.transform.smoothscale_by(img, scalar)
        img.set_alpha(None)
        pg.transform.threshold(img, img, (0,0,0), set_color=pg.Color(1,1,1), inverse_set=True)
        for piece in self.pieces.values():
            surf = self.make_piece_img(img, piece)
            piece.set_image(surf)
        for section in self.sections:
            for piece in section.pieces:
                surf = self.make_piece_img(img, piece)
                piece.set_image(surf)

    def make_pieces(self, puzzle_image:pg.Surface):
        self.pieces:dict[tuple[int, int], PuzzlePiece] = {}
        img_rect:pg.Rect = puzzle_image.get_rect()
        scalar = 800 / max(img_rect.size)
        pieceW = int(img_rect.w / 8 * scalar)
        pieceH = int(img_rect.h / 8 * scalar)
        for column in range(0, 8):
            for row in range(0, 8):
                self.pieces[(column, row)] = PuzzlePiece((column, row), (pieceW, pieceH))
        self.set_image(puzzle_image)
        for piece in self.pieces.values():
            piece.get_neighbors(self.pieces)

    def make_piece_img(self, image:pg.Surface, piece:PuzzlePiece):
        img_rect = image.get_rect()
        column, row = piece.index
        x = column * img_rect.w // 8
        y = row * img_rect.h // 8
        rect = pg.Rect(x - img_rect.h // 32, y - img_rect.h // 32,
                        3 * img_rect.w // 16, 3 * img_rect.h // 16)
        clipped = rect.clip(img_rect)
        offset = clipped.x - rect.x, clipped.y - rect.y
        surf = pg.Surface((3 * img_rect.w // 16, 3 * img_rect.h // 16))
        surf.blit(image.subsurface(clipped), offset)
        cover:pg.Surface = prepare.GFX[f"piece{column}-{row}"]
        cover = pg.transform.scale(cover, [3 * img_rect.w // 16, 3 * img_rect.h // 16])
        surf.blit(cover, (0, 0))
        surf.set_colorkey(pg.Color("black"))
        return surf

    def spread_pieces(self):
        screen_w, screen_h  = prepare.SCREEN_SIZE
        w = screen_w // 9
        h = screen_h // 9
        positions = [(x * w, y * h)
                for x in range(1, 9)
                for y in range(1, 9)]
        pieces = list(self.pieces.values())
        for piece in pieces:
            turns = randint(0, 3)
            piece.rotate(90 * turns)
        shuffle(pieces)
        for p, pos in zip(pieces, positions):
            p.set_pos(pos)
            
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
        piece2.set_pos(p2.center)
        section = PuzzleSection((piece1, piece2))
        indices = (piece1.index, piece2.index)
        for ind in indices:
            try:
                del self.pieces[ind]
            except KeyError:
                pass
        self.sections.append(section)
        
class HexPuzzle(Puzzle):
    def __init__(self, puzzle_image: pg.Surface, horizontalHexes):
        self.sections:list[HexPuzzleSection] = []
        self.make_pieces(puzzle_image, horizontalHexes)
        self.spread_pieces()

    def make_pieces(self, puzzle_image:pg.Surface, horizontalHexes:int):
        self.pieces:dict[tuple[int,int],HexPuzzlePiece] = {}
        img_rect:pg.Rect = puzzle_image.get_rect()
        scalar = 800 / max(img_rect.size)
        img_rect.width = scalar * img_rect.width
        img_rect.height = scalar * img_rect.height
        pieceW = img_rect.w / horizontalHexes
        hexSize = pieceW / sqrt(3)
        self.hexSize = hexSize
        pieceH = 2 * hexSize
        verticalHexes = ceil((img_rect.h - hexSize) / (1.5 * hexSize)) + 1
        self.horizontalHexes = horizontalHexes
        self.verticalHexes = verticalHexes
        for row in range(0, verticalHexes):
            rowParity = row % 2
            for column in range(0, horizontalHexes + rowParity):
                self.pieces[(column, row)] = HexPuzzlePiece((column, row), (int(pieceW), int(pieceH)))
        self.set_image(puzzle_image)
        for piece in self.pieces.values():
            piece.get_neighbors(self.pieces)
    
    def make_piece_img(self, image:pg.Surface, piece:HexPuzzlePiece):
        img_rect = image.get_rect()
        vSpacing = piece.size[1] * .75
        vertical_offset = (img_rect.h - (self.verticalHexes - 1) * vSpacing) / 2
        column, row = piece.index
        rowParity = row % 2
        x = (column - rowParity/2) * img_rect.w / self.horizontalHexes
        y = row * vSpacing + vertical_offset - piece.size[1] / 2
        rect = pg.Rect(x, y, piece.size[0], piece.size[1])
        clipped = rect.clip(img_rect)
        offset = clipped.x - rect.x, clipped.y - rect.y
        surf = pg.Surface(piece.size)
        surf.blit(image.subsurface(clipped), offset)
        hexSize = self.hexSize
        centerx, centery = piece.size[0] / 2, piece.size[1] / 2
        hexPoints = [(centerx + hexSize * sin(pi * i / 3),
                      centery + hexSize * cos(pi * i / 3)) for i in range(6)]
        cover = pg.Surface(piece.size)
        cover.fill("black")
        pg.draw.polygon(cover, "white", hexPoints)
        cover.set_colorkey("white")
        surf.blit(cover, (0, 0))
        surf.set_colorkey(pg.Color("black"))
        return surf

    def spread_pieces(self):
        screen_w, screen_h  = prepare.SCREEN_SIZE
        w = screen_w // 9
        h = screen_h // 9
        for piece in self.pieces.values():
            piece.set_pos((randint(w, w * 8), randint(h, h * 8)))
            turns = randint(0,5)
            piece.rotate(60 * turns)

    def join_pieces(self, piece1:HexPuzzlePiece, piece2:HexPuzzlePiece):
        p1 = pg.Rect((0, 0), piece1.size)
        p2 = p1.copy()
        p1.center = piece1.rect.center
        vSpacing = piece1.size[1] * 3 // 4
        for side in piece2.neighbors:
            rotatedSide = piece2.getRotatedSide(side)
            if piece1 is piece2.neighbors[side]:
                if rotatedSide == "left":
                    p2.left = p1.right
                    p2.top = p1.top
                elif rotatedSide == "right":
                    p2.right = p1.left
                    p2.top = p1.top
                elif rotatedSide == "topleft":
                    p2.centerx = p1.right
                    p2.top = p1.top + vSpacing
                elif rotatedSide == "topright":
                    p2.centerx = p1.left
                    p2.top = p1.top + vSpacing
                elif rotatedSide == "bottomleft":
                    p2.centerx = p1.right
                    p2.top = p1.top - vSpacing
                elif rotatedSide == "bottomright":
                    p2.centerx = p1.left
                    p2.top = p1.top - vSpacing
        piece2.set_pos(p2.center)
        section = HexPuzzleSection((piece1, piece2))
        indices = (piece1.index, piece2.index)
        for ind in indices:
            try:
                del self.pieces[ind]
            except KeyError:
                pass
        self.sections.append(section)

