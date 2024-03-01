import pygame as pg
import pygame_gui
import prepare
from state_engine import GameState
from puzzle import Puzzle, HexPuzzle
from pygame import camera
from pygame_gui.windows import ui_file_dialog
from PIL import Image
from tools import Animated

class Menu(GameState):
    def __init__(self):
        super(Menu, self).__init__()
        self.screen_rect = prepare.SCREEN_RECT
        self.manager = pygame_gui.UIManager(prepare.SCREEN_SIZE)
        self.persist["ui_manager"] = self.manager
        self.persist["shape"] = "puzzle"
        self.make_buttons()
        self.clicked_camera = False
        self.camera:camera.Camera

    def startup(self, persistent):
        self.persist = {}
        self.persist["ui_manager"] = self.manager
        self.persist["shape"] = "puzzle"
        self.manager.clear_and_reset()
        self.make_buttons()
        if persistent["mode"] == "camera":
            cam:camera.Camera = persistent["camera"]
            cam.stop()
            self.clicked_camera = False

    def make_buttons(self):
        self.buttons:list[pygame_gui.elements.UIButton] = []
        continents = sorted(prepare.CONTINENTS)
        w, h = 250, 80
        btn_rect = pg.Rect(0, 0, w, h)
        vert_space = 100
        left = self.screen_rect.centerx - w // 2
        top = self.screen_rect.centery - (h + vert_space * 5) // 2
        for continent in continents:
            self.buttons.append(pygame_gui.elements.UIButton(pg.Rect(left, top, w, h), continent, self.manager))
            top += vert_space
        top = self.screen_rect.centery - (h + vert_space * 5) // 2
        self.camera_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((100, top, w, h)), text='Camera', manager=self.manager)
        self.file_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((100, top + 100, w, h)), text='Choose Image', manager=self.manager)
        btn_rect.topright = (-50, 100)
        self.shape_dropdown = pygame_gui.elements.UIDropDownMenu(["puzzle", "hexagon"], "puzzle", btn_rect, self.manager, anchors={"right":"right", "top":"top"})
        btn_rect.topright = (-50, 200)
        self.hex_slider = pygame_gui.elements.UIHorizontalSlider(btn_rect, 8, (1, 20), self.manager, anchors={"right":"right", "top":"top"}, visible=0)
        self.hexes = 8
        btn_rect.topright = (-50, 300)
        self.hex_slide_label = pygame_gui.elements.UILabel(btn_rect, "8", self.manager, anchors={"right":"right", "top":"top"}, visible=0)

    def choose_map(self, continent:str):
        name = continent.replace(" ", "-")
        img:pg.Surface = prepare.GFX[name]
        self.persist["mode"] = "continent"
        if self.persist["shape"] == "puzzle":
            self.persist["puzzle"] = Puzzle(img)
        elif self.persist["shape"] == "hexagon":
            self.persist["puzzle"] = HexPuzzle(img, self.hexes)
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
        self.manager.clear_and_reset()
        pygame_gui.elements.UILabel(pg.Rect(0, 0, 250, 50), "Hold on...", self.manager, anchors={'center': 'center'})
        self.clicked_camera = True
    
    def choose_file(self, filePath:str):
        img = pg.image.load(filePath)
        self.persist["mode"] = "file"
        if self.persist["shape"] == "puzzle":
            self.persist["puzzle"] = Puzzle(img)
        elif self.persist["shape"] == "hexagon":
            self.persist["puzzle"] = HexPuzzle(img, self.hexes)
        self.next_state = "IDLE"
        self.done = True

    def choose_animated_file(self, filePath:str):
        with Image.open(filePath) as img:
            if img.n_frames==None or img.n_frames == 1:
                self.choose_file(filePath)
                return
            animation = Animated(img)
            self.persist["animation"] = animation
        self.persist["mode"] = "animation"
        if self.persist["shape"] == "puzzle":
            self.persist["puzzle"] = Puzzle(animation.first_frame())
        elif self.persist["shape"] == "hexagon":
            self.persist["puzzle"] = HexPuzzle(animation.first_frame(), self.hexes)
        self.next_state = "IDLE"
        self.done = True

    def get_event(self, event):
        if self.manager.process_events(event): return
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.quit = True
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                self.uifd = ui_file_dialog.UIFileDialog(prepare.SCREEN_RECT, self.manager, "Choose an image", {"png","jpg","gif","webp"}, allow_existing_files_only=True)
            elif event.ui_element == self.camera_button:
                self.choose_camera()
            else:
                for button in self.buttons:
                    if button.check_pressed():
                        self.choose_map(button.text)
        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.text[-3:] == "gif" or event.text[-4:] == "webp":
                self.choose_animated_file(event.text)
            else:
                self.choose_file(event.text)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self.persist["shape"] = event.text
            if event.text == "hexagon":
                self.hex_slider.show()
                self.hex_slide_label.show()
            else:
                self.hex_slider.hide()
                self.hex_slide_label.hide()
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self.hexes = event.value
            self.hex_slide_label.set_text(str(event.value))

    def update(self, dt):
        if self.clicked_camera:
            if self.camera.query_image():
                img = self.camera.get_image()
                if self.persist["shape"] == "puzzle":
                    self.persist["puzzle"] = Puzzle(img)
                elif self.persist["shape"] == "hexagon":
                    self.persist["puzzle"] = HexPuzzle(img, self.hexes)
                self.next_state = "IDLE"
                self.done = True
        self.manager.update(dt/1000)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.manager.draw_ui(surface)