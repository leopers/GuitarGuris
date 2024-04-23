import pygame
from note import Note  # Importação da classe Note para ser usada aqui
import time
class Song:

    def __init__(self, filename, game):

        self.chart = filename
        self.song_name = ''
        self.audio_stream = None
        self.game = game

        self.resolution = 0
        self.hopo_distance = 0
        self.offset = 0
        self.bpm = 0
        self.divisor = 0
        self.bps = 0
        self.tps = 0
        self.tpf = 0
        self.current_y = 0
        self.current_tick = 0

        self.pixels_per_second = 240
        self.pixels_per_beat = 0
        
        self.current_bpm = 0
        self.current_bpm_tick = 0
        self.bpm_list = []

        self.previous_note_hit = False

        self.note_list = []
        self.loaded_notes = []

        self.done = False
        self.time = 0

    #Loads a chart.
    def load_chart(self):
        with open(self.chart, 'rb') as infile:
            for line in infile:
                line = line.decode('utf-8').strip()
                if 'AudioStream' in line:
                    self.song_name = line[14:]
                    self.audio_stream = pygame.mixer.Sound(self.song_name)
                elif 'Resolution' in line:
                    self.resolution = int(line[13:])
                    self.hopo_distance = (65*self.resolution) / 192
                    #print self.hopo_distance
                elif 'Offset' in line:
                    self.offset = float(line[9:])
                elif 'BPM' in line:
                    self.bpm = int(line[6:])
                elif 'Divisor' in line:
                    self.divisor = float(line[10:])
                    #print self.divisor
                elif ' B ' in line:
                    line = line.split(' ')
                    tick = int(line[0])
                    bpm = int(line[-1]) / 1000.0
                    self.bpm_list.append((tick, bpm))
                elif ' N ' in line:
                    line = line.split(' ')
                    tick = int(line[0])
                    note_type = int(line[3])
                    color = ''
                    note_beat = (tick / float(self.resolution)) + self.offset
                    pixels_per_beat = (self.bpm/60.0) * 360
                    note_y = (720.0 - (note_beat * pixels_per_beat)) / self.divisor
                        
                    chord = False
                    sustain = 0
                    if int(line[-1]):
                        sustain = int(line[-1]) + tick
                        sustain_end_beat = (sustain / float(self.resolution)) + self.offset
                        sustain = (720.0 - (sustain_end_beat * pixels_per_beat)) / self.divisor
                        sustain = int(round(sustain))
                        #print sustain
                    if len(self.note_list) != 0:
                        if tick == self.note_list[-1].tick and note_type != 5:
                            chord = True
                            self.note_list[-1].chord = True
                        else:
                            chord = False
                    sustain_tick = int(line[-1])
                    #print note_beat, note_y
                    if note_type == 0:
                        color = 'green'
                        self.note_list.append(Note(tick, note_y, color, chord, self.game, sustain, sustain_tick))
                    elif note_type == 1:
                        color = 'red'
                        self.note_list.append(Note(tick, note_y, color, chord, self.game, sustain, sustain_tick))
                    elif note_type == 2:
                        color = 'yellow'
                        self.note_list.append(Note(tick, note_y, color, chord, self.game, sustain, sustain_tick))
                    elif note_type == 3:
                        color = 'blue'
                        self.note_list.append(Note(tick, note_y, color, chord, self.game, sustain, sustain_tick))
                    elif note_type == 4:
                        color = 'orange'
                        self.note_list.append(Note(tick, note_y, color, chord, self.game, sustain, sustain_tick))
                    elif note_type == 5:
                        if self.note_list[-1].hopo == True:
                            self.note_list[-1].hopo = False
                        else:
                            self.note_list[-1].hopo = True

        self.bps = self.bpm / 60.0
        self.tps = self.bps * self.resolution
        self.tpf = self.tps /60.0


    #Controls what notes are on screen, audio fadout, and end of song
    def update(self):

        self.current_y -= 6
        self.current_tick += self.tpf*1.04
        #The *1.04 is needed because the game generally runs at 58 FPS, and was falling behind
        self.current_tick
        for note in self.note_list:            
            if self.current_tick + (self.resolution*10) >= note.tick and note.dead == False and note not in self.loaded_notes:
                self.loaded_notes.append(note)
        for note in self.loaded_notes:
            if note.dead:
                self.loaded_notes.remove(note)


        if self.note_list[-1].dead and not self.done:
            self.audio_stream.fadeout(3000)
            self.done = True
            self.time = time.time()

        if self.done:
            if time.time() - self.time > 5:
                self.game.song_over = True