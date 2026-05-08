import pygame
import os
import config as cfg


class Animation:
    def __init__(self, filename, frame_w, frame_h, num_frames, fps=8, loop=True, start_frame=0):
        self.frames = []
        self.fps = fps
        self.loop = loop
        self.current_frame = 0
        self.frame_timer = 0
        self.start_frame = start_frame  # С какого кадра начинать

        path = os.path.join(cfg.SPRITES_PATH, filename)
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
            # Вырезаем кадры сверху вниз
            for i in range(start_frame, start_frame + num_frames):
                rect = pygame.Rect(0, i * frame_h, frame_w, frame_h)
                self.frames.append(sheet.subsurface(rect))
        else:
            print(f" Спрайт не найден: {path}")

    def update(self):
        if not self.frames:
            return

        # Если всего 1 кадр (сидение), ничего не делаем
        if len(self.frames) <= 1:
            return

        self.frame_timer += 1
        # Скорость: меняем кадр каждые (60 / fps) кадров игры
        if self.frame_timer >= max(1, 60 // self.fps):
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0 if self.loop else len(self.frames) - 1
            self.frame_timer = 0

    def get_frame(self):
        return self.frames[self.current_frame] if self.frames else None
