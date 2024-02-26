import pygame as pg
import pygame_gui
import prepare
from state_engine import GameState
from labels import Button, ButtonGroup, Label
from puzzle import Puzzle
from pygame import camera
from pygame_gui.windows import ui_file_dialog
from PIL import Image
from tools import Animated

class Menu(GameState):
    def __init__(self):
        super(Menu, self).__init__()
        self.screen_rect = prepare.SCREEN_RECT
        self.manager = pygame_gui.UIManager(prepare.SCREEN_SIZE)
        self.make_buttons()
        self.clicked_camera = False
        self.camera:camera.Camera

    def startup(self, persistent):
        self.persist = {}
        if persistent["mode"] == "camera":
            cam:camera.Camera = persistent["camera"]
            cam.stop()
            self.clicked_camera = False

    def make_buttons(self):
        self.buttons = ButtonGroup()
        style = {"fill_color": pg.Color("gray10"),
                 "hover_fill_color": pg.Color("gray20"),
                 "text_color": pg.Color("gray80"),
                 "hover_text_color": pg.Color("gray90")}
        continents = sorted(prepare.CONTINENTS)
        w, h = 250, 80
        vert_space = 100
        left = self.screen_rect.centerx - w // 2
        top = self.screen_rect.centery - (h + vert_space * 5) // 2
        for continent in continents:
            Button((left, top, w, h), self.buttons, text=continent, 
                      hover_text=continent, call=self.choose_map,
                      args=continent, **style)
            top += vert_space
        top = self.screen_rect.centery - (h + vert_space * 5) // 2
        self.camera_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((100, top, w, h)),
                                                        text='Camera', manager=self.manager)
        self.file_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((100, top + 100, w, h)),
                                                        text='Choose Image', manager=self.manager)

    def choose_map(self, continent:str):
        name = continent.replace(" ", "-")
        img:pg.Surface = prepare.GFX[name]
        scalar = 850 / max(img.get_size()) 
        img = pg.transform.smoothscale_by(img, scalar)
        self.persist["mode"] = "continent"
        self.persist["puzzle"] = Puzzle(img)
        self.next_state = "IDLE"
        self.done = True

    def choose_camera(self):
        camera.init()
        cameras = camera.list_cameras()
        self.camera = camera.Camera(cameras[0])
        self.persist["mode"] = "camera"
        self.persist["camera"] = self.camera
        self.camera.start()
        self.camera.set_controls(hflip=True)
        self.clicked_camera = True
    
    def choose_file(self, filePath:str):
        img = pg.image.load(filePath)
        scalar = 850 / max(img.get_size())
        img = img.convert(24)
        img = pg.transform.smoothscale_by(img, scalar)
        self.persist["mode"] = "file"
        self.persist["puzzle"] = Puzzle(img)
        self.next_state = "IDLE"
        self.done = True

    def choose_gif_file(self, filePath:str):
        with Image.open(filePath) as img:
            if img.n_frames==None or img.n_frames == 1:
                self.choose_file(filePath)
                return
            gif = Animated(img)
            self.persist["gif"] = gif
        self.persist["mode"] = "gif"
        self.persist["puzzle"] = Puzzle(gif.first_frame())
        self.next_state = "IDLE"
        self.done = True

    def get_event(self, event):
        if self.manager.process_events(event): return
        self.buttons.get_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.quit = True
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                self.uifd = ui_file_dialog.UIFileDialog(prepare.SCREEN_RECT, self.manager, "Choose an image",
                    {"png","jpg","gif","webp"}, allow_existing_files_only=True)
            elif event.ui_element == self.camera_button:
                self.choose_camera()
        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.text[-3:] == "gif" or event.text[-4:] == "webp":
                self.choose_gif_file(event.text)
            else:
                self.choose_file(event.text)

    def update(self, dt):
        if self.clicked_camera:
            if self.camera.query_image():
                img = self.camera.get_image()
                self.persist["puzzle"] = Puzzle(img)
                self.next_state = "IDLE"
                self.done = True
            return
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        self.manager.update(dt/1000)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        if self.clicked_camera:
            Label(None, 36, "Hold on...", "lightgreen", {"center":self.screen_rect.center}).draw(surface)
            return
        self.buttons.draw(surface)
        self.manager.draw_ui(surface)
