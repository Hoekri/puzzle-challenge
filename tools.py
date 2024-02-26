import os
import copy
import pygame as pg
from PIL import ImageSequence
from puzzle import Puzzle

class Animated:
    def __init__(self, image) -> None:
        self.frames = []
        self.durations = []
        for frame in ImageSequence.Iterator(image):
            frame.save(f"./resources/temp/frame.png")
            pgFrame = pg.image.load(f"./resources/temp/frame.png")
            self.frames.append(pgFrame)
            self.durations.append(frame.info["duration"])
        self.index = 0
        self.duration = 0

    def first_frame(self): return self.frames[0]

    def update(self, puzzle:Puzzle, dt:int):
        self.duration += dt
        if self.duration < self.durations[self.index]:
            return
        self.index = (self.index + 1) % len(self.frames)
        puzzle.set_image(self.frames[self.index])
        self.duration = 0

class _KwargMixin(object):
    """
    Useful for classes that require a lot of keyword arguments for
    customization.
    """
    def process_kwargs(self, name, defaults, kwargs):
        """
        Arguments are a name string (displayed in case of invalid keyword);
        a dictionary of default values for all valid keywords;
        and the kwarg dict.
        """
        settings = copy.deepcopy(defaults)
        for kwarg in kwargs:
            if kwarg in settings:
                if isinstance(kwargs[kwarg], dict):
                    settings[kwarg].update(kwargs[kwarg])
                else:
                    settings[kwarg] = kwargs[kwarg]
            else:
                message = "{} has no keyword: {}"
                raise AttributeError(message.format(name, kwarg))
        for setting in settings:
            setattr(self, setting, settings[setting])


def load_all_gfx(directory,colorkey=(0,0,0),accept=(".png",".jpg",".bmp")):
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics


def load_all_music(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    songs = {}
    for song in os.listdir(directory):
        name,ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs
            
def load_all_sfx(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    effects = {}
    for fx in os.listdir(directory):
        name,ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects

def load_all_fonts(directory, accept=(".ttf")):
    return load_all_music(directory, accept)
    

def strip_from_sheet(sheet, start, size, columns, rows=1):
    """
    Strips individual frames from a sprite sheet given a start location,
    sprite size, and number of columns and rows.
    """
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0]+size[0]*i, start[1]+size[1]*j)
            frames.append(sheet.subsurface(pg.Rect(location, size)))
    return frames
    
    
