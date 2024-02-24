import pygame as pg
from state_engine import GameState
from puzzle import Puzzle
from labels import Blinker, Button

class Idle(GameState):
    def __init__(self):
        super(Idle, self).__init__()
        
    def startup(self, persistent):
        self.persist = persistent
        self.puzzle:Puzzle = self.persist["puzzle"]
        self.sections = self.puzzle.sections
        self.pieces = self.puzzle.pieces.values()
        self.puzzle_finished = False
        self.menuButton = Button((50, 150, 250, 50), text="Back to menu?", fill_color= pg.Color("gray10"),
                 hover_fill_color= pg.Color("gray20"), text_color= pg.Color("gray80"),
                 hover_text_color= pg.Color("gray90"), hover_text="Back to menu!", call= self.to_menu)
        self.congratulations = Blinker(None, 36, "Congrats, you did it!", "lightgreen", {"topleft":(50, 50)}, 1000, "grey10")
        if len(self.sections) + len(self.pieces) == 1:
            self.puzzle_finished = True

    def get_event(self, event):
        self.menuButton.get_event(event)
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for section in self.puzzle.sections:
                if section.grab(event.pos):
                    self.persist["grabbed_piece"] = section
                    self.next_state = "DRAGGING_SECTION"
                    self.done = True
                    return
            for piece in self.pieces:
                if piece.rect.collidepoint(event.pos):
                    piece.grabbed = True
                    self.persist["grabbed_piece"] = piece
                    self.next_state = "DRAGGING_PIECE"
                    self.done = True
                    return
    
    def update(self, dt):
        self.congratulations.update(dt)
        mouse_pos = pg.mouse.get_pos()
        self.menuButton.update(mouse_pos)
        
    def draw(self, surface:pg.Surface):
        surface.fill(pg.Color("black"))
        self.puzzle.draw(surface)
        if self.puzzle_finished:
            self.congratulations.draw(surface)
            self.menuButton.draw(surface) # hover text

    def to_menu(self, none=None):
        self.next_state = "MENU"
        self.done = True
    