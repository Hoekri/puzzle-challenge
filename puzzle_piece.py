import pygame as pg
from typing import Self

def close_enough(value, target, tolerance=7):
    return target - tolerance <= value <= target + tolerance

class PuzzlePiece(object):
    def __init__(self, index, size):
        self.index = index
        self.image:pg.Surface
        self.collision_rect = pg.Rect((0, 0), size)
        self.rect = pg.Rect((index[0]*size[0], index[1]*size[1]), (0, 0))
        self.grabbed = False
        self.grab_offset:tuple
        self.orientation = 0
    
    def set_pos(self, pos):
        self.rect.center = pos
        
    def get_neighbors(self, piece_dict):
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
   
    def is_joinable(self, other):
        if self.orientation != other.orientation:
            return False
        for side in self.neighbors:
            rotatedSide = self.getRotatedSide(side)
            if other is self.neighbors[side]:
                r1 = pg.Rect((0,0), self.collision_rect.size)
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
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def rotate(self, degrees):
        assert degrees % 90 == 0
        ndts = degrees // 90
        self.image = pg.transform.rotate(self.image, degrees)
        self.rect = self.image.get_rect()
        w, h = self.collision_rect.size # TODO maps are broken and fixed with below
        # if ndts % 2 == 1: self.collision_rect = pg.Rect((0,0), (h, w)) # but this breaks camera
        self.orientation = (self.orientation + degrees // 90) % 4

    def getRotatedSide(self, side:str):
        return [{"left":"left","right":"right","top":"top","bottom":"bottom"},
                {"left":"bottom","right":"top","top":"left","bottom":"right"},
                {"left":"right","right":"left","top":"bottom","bottom":"top"},
                {"left":"top","right":"bottom","top":"right","bottom":"left"}
                ][self.orientation][side]
    
    def set_image(self, image):
        self.image = pg.transform.rotate(image, self.orientation * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

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
            if piece.rect.collidepoint(mouse_pos):
                self.grabbed_piece = piece
                for piece_ in self.pieces:
                    piece_.grab_offset = piece_.rect.centerx - mouse_pos[0], piece_.rect.centery - mouse_pos[1]
                self.grabbed = True
                return True
        return False

    def set_pos(self, pos:tuple):
        for piece in self.pieces:
            x, y = piece.grab_offset
            piece.rect.center = pos[0] + x, pos[1] + y

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
        
    def add_piece(self, piece:PuzzlePiece, loose_pieces:dict[tuple,PuzzlePiece]):
        for s_piece in self.pieces:
            for side in piece.neighbors:
                rotatedSide = piece.getRotatedSide(side)
                if s_piece is piece.neighbors[side]:
                    p1 = pg.Rect((0, 0), piece.collision_rect.size)
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
                    piece.rect.center = p2.center
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
                        p1 = pg.Rect((0, 0), piece.collision_rect.size)
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
                            piece_.rect.move_ip(x_diff, y_diff)
                            self.pieces.append(piece_)
                        self.grabbed = False
                        return

    def get_event(self, event:pg.Event):       
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.grabbed:
                self.release()

    def draw(self, surface:pg.Surface):
        for piece in self.pieces:
            piece.draw(surface)

    def rotate(self, degrees:int):
        assert degrees % 90 == 0
        ndts = (degrees // 90) % 4
        for piece in self.pieces:
            piece.rotate(degrees)
            piece.grab_offset = [(piece.grab_offset[0], piece.grab_offset[1]),
                                 (piece.grab_offset[1], -piece.grab_offset[0]),
                                 (-piece.grab_offset[0], -piece.grab_offset[1]),
                                 (-piece.grab_offset[1], piece.grab_offset[0])][ndts]
    
