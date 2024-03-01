import pygame as pg
import prepare
from puzzle import Puzzle
from puzzle_piece import PuzzlePiece
from state_engine import GameState
from pygame import camera

class DraggingPiece(GameState):
    def __init__(self):
        super(DraggingPiece, self).__init__()
        
    def startup(self, persistent):
        self.persist = persistent
        self.puzzle:Puzzle = self.persist["puzzle"]
        self.sections = self.puzzle.sections
        self.pieces = self.puzzle.pieces.values()
        self.grabbed:PuzzlePiece = self.persist["grabbed_piece"]

    def check_pieces(self):
        """
        Checks whether self.grabbed (the piece controlled by the
        player) can be joined with any of the other unjoined
        pieces. If so, the pieces are joined and True is returned.
        Returns False if the piece cannot be joined with any others.
        """
        for piece in self.pieces:
            if self.grabbed.is_joinable(piece):
                self.puzzle.join_pieces(self.grabbed, piece)
                return True
        return False
        
    def check_sections(self): 
        """
        Similar to check_pieces but checks whether self.grabbed can be
        joined with any of the existing puzzle sections. If it can be joined
        it is added to the section and True is returned. Returns False if
        the piece cannot be added to any of the sections.
        """
        for section in self.sections:
            if section.can_add(self.grabbed):
                section.add_piece(self.grabbed, self.puzzle.pieces)
                return True
        return False
                    
    def get_event(self, event:pg.Event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.next_state = "MENU"
            self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.check_pieces():
                self.check_sections()
            self.grabbed.grabbed = False
            self.done = True
            self.next_state = "IDLE"
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            self.grabbed.rotate()
        
    def update(self, dt:int):
        if self.persist["mode"] == "camera":
            cam:camera.Camera = self.persist["camera"]
            if cam.query_image():
                self.puzzle.set_image(cam.get_image())
        elif self.persist["mode"] == "animation":
            self.persist["animation"].update(self.puzzle, dt)
        mouse_pos = pg.mouse.get_pos()
        x = mouse_pos[0] + self.grabbed.rect.centerx - self.grabbed.collision.centerx
        y = mouse_pos[1] + self.grabbed.rect.centery - self.grabbed.collision.centery
        self.grabbed.set_pos((x, y))
        
    def draw(self, surface:pg.Surface):
        surface.fill(pg.Color("grey10"))
        self.puzzle.draw(surface)
        self.grabbed.draw(surface)