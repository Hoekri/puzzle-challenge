import pygame as pg
import prepare
            
class GameState(object):
    """
    Parent class for individual game states to inherit from. 
    """
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state:str
        self.screen_rect = pg.display.get_surface().get_rect()
        self.persist = {}
        self.font = pg.font.Font(None, 24)
        
    def startup(self, persistent:dict):
        """
        Called when a state resumes being active.
        Allows information to be passed between states.
        
        persistent: a dict passed from state to state
        """
        self.persist = persistent        
        
    def get_event(self, event:pg.Event):
        """
        Handle a single event passed by the Game object.
        """
        pass
    
    def update(self, dt:int):
        """
        Update the state. Called by the Game object once
        per frame. 
        
        dt: time since last frame
        """
        pass
        
    def draw(self, surface:pg.Surface):
        """
        Draw everything to the screen.
        """
        pass
    
class Game(object):
    """
    A single instance of this class is responsible for 
    managing which individual game state is active
    and keeping it updated. It also handles many of
    pygame's nuts and bolts (managing the event 
    queue, framerate, updating the display, etc.). 
    and its run method serves as the "game loop".
    """
    def __init__(self, screen:pg.Surface, states:dict[str, GameState], start_state:str):
        """
        Initialize the Game object.
        
        screen: the pygame display surface
        states: a dict mapping state-names to GameState objects
        start_state: name of the first active game state 
        """
        self.done = False
        self.screen = screen
        self.clock = pg.time.Clock()
        self.fps = 60
        self.states:dict[str, GameState] = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.fullscreen = False
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pg.display.set_mode(prepare.SCREEN_SIZE, pg.FULLSCREEN)
        else:            
            self.screen = pg.display.set_mode(prepare.SCREEN_SIZE)        
    
    def event_loop(self):
        """Events are passed for handling to the current state."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN and event.key == pg.K_f:
                self.toggle_fullscreen()
            self.state.get_event(event)
            
    def flip_state(self):
        """Switch to the next game state."""
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)
        
    def update(self, dt:int):
        """
        Check for state flip and update active state.
        
        dt: milliseconds since last frame
        """
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()    
        self.state.update(dt)
        
    def draw(self):
        """Pass display surface to active state for drawing."""
        self.state.draw(self.screen)
        
    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """ 
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pg.display.update()
