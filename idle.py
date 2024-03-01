import pygame as pg
from state_engine import GameState
from puzzle import Puzzle
import pygame_gui
from pygame_gui import ui_manager
from pygame import camera
from tools import Animated

class Idle(GameState):
    def __init__(self):
        super(Idle, self).__init__()

    def startup(self, persistent):
        self.persist = persistent
        self.puzzle:Puzzle = self.persist["puzzle"]
        self.mode = self.persist["mode"]
        self.manager:ui_manager.UIManager = self.persist["ui_manager"]
        self.manager.clear_and_reset()
        if self.mode == "camera": self.camera:camera.Camera = self.persist["camera"]
        if self.mode == "animation": self.animation:Animated = self.persist["animation"]
        self.sections = self.puzzle.sections
        self.pieces = self.puzzle.pieces.values()
        self.menuButton = pygame_gui.elements.UIButton(pg.Rect(50, 150, 250, 50), "Back to menu", manager=self.manager, visible=0)
        self.congratulations = pygame_gui.elements.UILabel(pg.Rect(50, 50, 250, 50), "Congrats, you did it!", manager=self.manager, visible=0)
        if len(self.sections) + len(self.pieces) == 1:
            self.menuButton.show()
            self.congratulations.show()

    def get_event(self, event):
        self.manager.process_events(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.next_state = "MENU"
            self.done = True
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.next_state = "MENU"
            self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for piece in self.pieces:
                if piece.collision.collidepoint(event.pos):
                    piece.grabbed = True
                    self.persist["grabbed_piece"] = piece
                    self.next_state = "DRAGGING_PIECE"
                    self.done = True
                    return
            for section in self.puzzle.sections:
                if section.grab(event.pos):
                    self.persist["grabbed_piece"] = section
                    self.next_state = "DRAGGING_SECTION"
                    self.done = True
                    return

    def update(self, dt):
        if self.mode == "camera":
            if self.camera.query_image():
                self.puzzle.set_image(self.camera.get_image())
        elif self.mode == "animation":
            self.animation.update(self.puzzle, dt)
        self.manager.update(dt/1000)

    def draw(self, surface:pg.Surface):
        surface.fill(pg.Color("grey10"))
        self.puzzle.draw(surface)
        self.manager.draw_ui(surface)
