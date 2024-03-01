import pygame as pg
from puzzle import Puzzle
from puzzle_piece import PuzzleSection
from state_engine import GameState


class DraggingSection(GameState):
    def __init__(self):
        super(DraggingSection, self).__init__()

    def startup(self, persistent):
        self.persist = persistent
        self.puzzle:Puzzle = self.persist["puzzle"]
        self.sections = self.puzzle.sections
        self.pieces = self.puzzle.pieces.values()
        self.grabbed:PuzzleSection = self.persist["grabbed_piece"]
   
    def leave_state(self, next_state):
        self.done = True
        self.next_state = next_state
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.next_state = "MENU"
            self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for section in [x for x in self.sections if x is not self.grabbed]:
                if self.grabbed.can_add_section(section):
                    self.grabbed.add_section(section)
                    self.sections.remove(section)
                    self.grabbed.release()
                    self.leave_state("IDLE")
                    return
            for piece in self.pieces:
                if self.grabbed.can_add(piece):
                    self.grabbed.add_piece(piece, self.puzzle.pieces)
                    self.grabbed.release()
                    self.leave_state("IDLE")
                    return
            self.leave_state("IDLE")
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            self.grabbed.rotate()
        
    def update(self, dt):
        if self.persist["mode"] == "camera":
            cam = self.persist["camera"]
            if cam.query_image():
                self.puzzle.set_image(cam.get_image())
        elif self.persist["mode"] == "animation":
            self.persist["animation"].update(self.puzzle, dt)
        mouse_pos = pg.mouse.get_pos()
        self.grabbed.set_pos(mouse_pos)

    def draw(self, surface):
        surface.fill(pg.Color("grey10"))
        self.puzzle.draw(surface)