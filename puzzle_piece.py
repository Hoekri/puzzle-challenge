import pygame as pg
from typing import Self
from math import radians, cos, sin

def close_enough(value, target, tolerance=7):
    return target - tolerance <= value <= target + tolerance

class PuzzlePiece(object):
    def __init__(self, index:tuple[int,int], size:tuple[int,int]):
        self.index = index
        self.image:pg.Surface
        self.size = size
        self.rect = pg.Rect((index[0]*size[0], index[1]*size[1]), size)
        self.collision = self.rect.copy()
        self.grabbed = False
        self.grab_offset:tuple
        self.orientation = 0

    def set_pos(self, pos:tuple[int, int]):
        old = self.rect.center
        self.rect.center = pos
        new = self.rect.center
        self.collision.move_ip(new[0] - old[0], new[1] - old[1])

    def move_ip(self, delta:tuple[int,int]):
        self.rect.move_ip(delta)
        self.collision.move_ip(delta)

    def get_neighbors(self, piece_dict:dict[tuple[int,int],Self]):
        self.neighbors = {}
        offsets = ((-1, 0), (1, 0), (0, -1), (0, 1))
        directions = ("left", "right", "top", "bottom")
        sides = {offset: direct for offset, direct in zip(offsets, directions)}
        for offset in offsets:
            neighbor_index = self.index[0] + offset[0], self.index[1] + offset[1]
            try:
                neighbor = piece_dict[neighbor_index]
            except KeyError:
                neighbor = None
            self.neighbors[sides[offset]] = neighbor

    def is_joinable(self, other:Self):
        if self.orientation != other.orientation:
            return False
        for side in self.neighbors:
            rotatedSide = self.getRotatedSide(side)
            if other is self.neighbors[side]:
                r1 = pg.Rect((0,0), self.size)
                r2 = r1.copy()
                r1.center = self.rect.center
                r2.center = other.rect.center
                pos_pairs = {
                        "left": ((r1.left, r2.right), (r1.top, r2.top)),
                        "right": ((r1.right, r2.left), (r1.top, r2.top)),
                        "top": ((r1.left, r2.left), (r1.top, r2.bottom)),
                        "bottom": ((r1.left, r2.left), (r1.bottom, r2.top))}
                if all((close_enough(*pair) for pair in pos_pairs[rotatedSide])):
                    return True
        return False

    def draw(self, surface:pg.Surface):
        surface.blit(self.image, self.rect)

    def rotate(self, degrees=90):
        assert degrees % 90 == 0
        ndts = degrees // 90
        self.image = pg.transform.rotate(self.image, degrees)
        self.rect = self.image.get_rect()
        self.collision = self.image.get_bounding_rect()
        self.collision.move_ip(self.rect.topleft)
        self.orientation = (self.orientation + ndts) % 4

    def getRotatedSide(self, side:str):
        return [{"left":"left","right":"right","top":"top","bottom":"bottom"},
                {"left":"bottom","right":"top","top":"left","bottom":"right"},
                {"left":"right","right":"left","top":"bottom","bottom":"top"},
                {"left":"top","right":"bottom","top":"right","bottom":"left"}
                ][self.orientation][side]
    
    def set_image(self, image:pg.Surface):
        self.image = pg.transform.rotate(image, self.orientation * 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.collision = self.image.get_bounding_rect()
        self.collision.move_ip(self.rect.topleft)

class PuzzleSection(object):
    def __init__(self, pieces:tuple[PuzzlePiece, PuzzlePiece]):
        """A group of PuzzlePieces that have been connected together."""
        self.pieces:list[PuzzlePiece] = list(pieces)
        self.grabbed = False
        self.grab_offset = (0, 0)
        self.grabbed_piece = None
        self.orientation = pieces[0].orientation

    def grab(self, mouse_pos:tuple):
        for piece in self.pieces:
            if piece.collision.collidepoint(mouse_pos):
                self.grabbed_piece = piece
                for piece_ in self.pieces:
                    piece_.grab_offset = piece_.rect.centerx - mouse_pos[0], piece_.rect.centery - mouse_pos[1]
                self.grabbed = True
                return True
        return False

    def set_pos(self, pos:tuple):
        for piece in self.pieces:
            x, y = piece.grab_offset
            piece.set_pos((pos[0] + x, pos[1] + y))

    def release(self):
        self.grabbed = False
        for piece in self.pieces:
            piece.grab_offset = (0, 0)

    def can_add(self, piece:PuzzlePiece):
        return any((piece.is_joinable(s_piece) for s_piece in self.pieces))
          
    def can_add_section(self, section:Self):
        for piece in section.pieces:
            if self.can_add(piece):
                return True
        return False
        
    def add_piece(self, piece:PuzzlePiece, loose_pieces:dict[tuple[int,int],PuzzlePiece]):
        for s_piece in self.pieces:
            for side in piece.neighbors:
                rotatedSide = piece.getRotatedSide(side)
                if s_piece is piece.neighbors[side]:
                    p1 = pg.Rect((0, 0), piece.size)
                    p2 = p1.copy()
                    p1.center = s_piece.rect.center
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
                    piece.set_pos(p2.center)
                    self.pieces.append(piece)
                    piece.grabbed = False
                    index_ = piece.index
                    del loose_pieces[index_]
                    return                    
        
    def add_section(self, other_section:Self):
        other_pieces = other_section.pieces
        for other_piece in other_pieces:
            for piece in self.pieces:
                for side in piece.neighbors:
                    rotatedSide = piece.getRotatedSide(side)
                    if other_piece is piece.neighbors[side]:
                        p1 = pg.Rect((0, 0), piece.size)
                        p2 = p1.copy()
                        p1.center = piece.rect.center
                        p2.center = other_piece.rect.center
                        if rotatedSide == "left":
                            x_diff = p1.left - p2.right
                            y_diff = p1.top - p2.top
                        elif rotatedSide == "right":
                            x_diff = p1.right - p2.left
                            y_diff = p1.top - p2.top
                        elif rotatedSide == "top":
                            y_diff = p1.top - p2.bottom
                            x_diff = p1.left - p2.left
                        elif rotatedSide == "bottom":
                            y_diff = p1.bottom - p2.top
                            x_diff = p1.left - p2.left
                        for piece_ in other_section.pieces:
                            piece_.move_ip((x_diff, y_diff))
                            self.pieces.append(piece_)
                        self.grabbed = False
                        return

    def draw(self, surface:pg.Surface):
        for piece in self.pieces:
            piece.draw(surface)

    def rotate(self, degrees=90):
        assert degrees % 90 == 0
        ndts = (degrees // 90) % 4
        for piece in self.pieces:
            piece.rotate(degrees)
            piece.grab_offset = [(piece.grab_offset[0], piece.grab_offset[1]),
                                 (piece.grab_offset[1], -piece.grab_offset[0]),
                                 (-piece.grab_offset[0], -piece.grab_offset[1]),
                                 (-piece.grab_offset[1], piece.grab_offset[0])][ndts]
    
class HexPuzzlePiece(PuzzlePiece):
    def get_neighbors(self, piece_dict:dict[tuple[int,int],Self]):
        self.neighbors = {}
        parity = self.index[1] % 2
        offsets = [((-1, 0), (1, 0), (0, -1), (1, -1), (0, 1), (1, 1)),
                   ((-1, 0), (1, 0), (-1, -1), (0, -1), (-1, 1), (0, 1))][parity]
        directions = ("left", "right", "topleft", "topright", "bottomleft", "bottomright")
        sides = {offset: direct for offset, direct in zip(offsets, directions)}
        for offset in offsets:
            neighbor_index = self.index[0] + offset[0], self.index[1] + offset[1]
            try:
                neighbor = piece_dict[neighbor_index]
            except KeyError:
                neighbor = None
            self.neighbors[sides[offset]] = neighbor

    def is_joinable(self, other: Self):
        if self.orientation != other.orientation:
            return False
        vSpacing = self.size[1] * 3 / 4
        for side in self.neighbors:
            rotatedSide = self.getRotatedSide(side)
            if other is self.neighbors[side]:
                r1 = pg.Rect((0,0), self.size)
                r2 = r1.copy()
                r1.center = self.rect.center
                r2.center = other.rect.center
                pos_pairs = {
                        "left": ((r1.left, r2.right), (r1.top, r2.top)),
                        "right": ((r1.right, r2.left), (r1.top, r2.top)),
                        "topleft": ((r1.left, r2.centerx), (r1.top - r2.top, vSpacing)),
                        "topright": ((r1.right, r2.centerx), (r1.top - r2.top, vSpacing)),
                        "bottomleft": ((r1.left, r2.centerx), (r2.top - r1.top, vSpacing)),
                        "bottomright": ((r1.right, r2.centerx), (r2.top - r1.top, vSpacing))}
                if all((close_enough(*pair) for pair in pos_pairs[rotatedSide])):
                    return True
        return False
    
    def rotate(self, degrees=60):
        assert degrees % 60 == 0
        self.orientation = (self.orientation + degrees // 60) % 6
        self.image = pg.transform.rotate(self.upright_image, self.orientation * 60)
        self.collision = self.image.get_bounding_rect()
        self.collision.move_ip(self.rect.topleft)
    
    def getRotatedSide(self, side: str):
        sides = ["right","topright","topleft","left","bottomleft","bottomright"]
        sideIndex = sides.index(side)
        rotatedIndex = (sideIndex + self.orientation) % 6
        return sides[rotatedIndex]
    
    def set_image(self, image: pg.Surface):
        self.upright_image = image
        self.image = pg.transform.rotate(image, self.orientation * 60)
        self.collision = self.image.get_bounding_rect()
        self.collision.move_ip(self.rect.topleft)

class HexPuzzleSection(PuzzleSection):
    def add_piece(self, piece, loose_pieces):
        vSpacing = piece.size[1] * 3 / 4
        for s_piece in self.pieces:
            for side in piece.neighbors:
                rotatedSide = piece.getRotatedSide(side)
                if s_piece is piece.neighbors[side]:
                    p1 = pg.Rect((0, 0), piece.size)
                    p2 = p1.copy()
                    p1.center = s_piece.rect.center
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
                    piece.set_pos(p2.center)
                    self.pieces.append(piece)
                    piece.grabbed = False
                    index_ = piece.index
                    del loose_pieces[index_]
                    return
    
    def add_section(self, other_section: Self):
        other_pieces = other_section.pieces
        vSpacing = other_pieces[0].size[1] * 3 / 4
        for other_piece in other_pieces:
            for piece in self.pieces:
                for side in piece.neighbors:
                    rotatedSide = piece.getRotatedSide(side)
                    if other_piece is piece.neighbors[side]:
                        p1 = pg.Rect((0, 0), piece.size)
                        p2 = p1.copy()
                        p1.center = piece.rect.center
                        p2.center = other_piece.rect.center
                        if rotatedSide == "left":
                            y_diff = p1.top - p2.top
                            x_diff = p1.left - p2.right
                        elif rotatedSide == "right":
                            y_diff = p1.top - p2.top
                            x_diff = p1.right - p2.left
                        elif rotatedSide == "topleft":
                            y_diff = p1.top - p2.top - vSpacing
                            x_diff = p1.left - p2.centerx
                        elif rotatedSide == "topright":
                            y_diff = p1.top - p2.top - vSpacing
                            x_diff = p1.right - p2.centerx
                        elif rotatedSide == "bottomleft":
                            y_diff = p1.top - p2.top + vSpacing
                            x_diff = p1.left - p2.centerx
                        elif rotatedSide == "bottomright":
                            y_diff = p1.top - p2.top + vSpacing
                            x_diff = p1.right - p2.centerx
                        for piece_ in other_section.pieces:
                            piece_.rect.move_ip(x_diff, y_diff)
                            self.pieces.append(piece_)
                        self.grabbed = False
                        return
    
    def rotate(self, degrees=60):
        assert degrees % 60 == 0
        rad = -radians(degrees)
        for piece in self.pieces:
            piece.rotate(degrees)
            x, y = piece.grab_offset
            piece.grab_offset = (x * cos(rad) - y * sin(rad),
                                 x * sin(rad) + y * cos(rad))
