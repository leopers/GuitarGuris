import pygame
from pygame.locals import *

class Note(pygame.sprite.Sprite):
    def __init__(self, tick, y, color, chord, game, sustain, sustain_tick):
        super().__init__()
        self.tick = tick
        self.y = y
        self.color = color
        self.chord = chord
        self.game = game
        self.sustain = sustain != 0
        self.sustain_tick = sustain_tick
        self.sustain_y = sustain
        self.held = False
        self.speed = 6
        self.dead = False
        self.missed = False
        self.hopo = self.determine_hopo(chord, game)

        # Assign color based positions
        self.x = self.assign_x_position(color)
        self.image = pygame.Surface([40, 40])
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def assign_x_position(self, color):
        color_positions = {
            'green': 540,
            'red': 590,
            'yellow': 640,
            'blue': 690,
            'orange': 740
        }
        return color_positions.get(color, 0)

    def determine_hopo(self, chord, game):
        if chord:
            return game.song.note_list[-1].hopo
        elif game.song.note_list and self.tick - game.song.note_list[-1].tick <= game.song.hopo_distance:
            return game.song.note_list[-1].color != self.color
        return False

    def update(self):
        self.rect.y += self.speed
        if self.sustain:
            self.sustain_y += self.speed

        if self.rect.center[1] > 830 and not self.dead:
            self.handle_miss()

    def handle_miss(self):
        if self.sustain and self.sustain_y > 830:
            self.mark_note_dead()
        elif not self.sustain:
            self.mark_note_dead()

        if self.rect.center[1] > 740 and not self.dead and not self.missed:
            self.miss_note()

    def miss_note(self):
        self.game.song.previous_note_hit = False
        self.missed = True
        self.game.multiplier = 1
        self.game.partial_multiplier = 0

    def mark_note_dead(self):
        self.game.song.loaded_notes.remove(self)
        self.dead = True
        self.kill()
        if not self.sustain:
            self.game.multiplier = 1
            self.game.partial_multiplier = 0