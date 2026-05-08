import pygame
import config as cfg
from .animation import Animation


class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Параметры спрайта
        W, H = 57, 64

        # Анимации
        self.animations = {
            # Бег: кадры 0-3
            'run': Animation('cat_run.png', W, H, num_frames=4, fps=2, loop=True, start_frame=0),
            # Сидение: кадр 4
            'idle': Animation('cat_run.png', W, H, num_frames=1, fps=1, loop=True, start_frame=4)
        }

        self.current_animation = 'idle'
        self.x = float(x)
        self.y = float(y)

        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.facing_right = True

        self.width = W
        self.height = H
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, keys, platforms=None):
        # 1. Управление
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -cfg.SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = cfg.SPEED
            self.facing_right = True

        # 2. Гравитация
        if not self.on_ground:
            self.velocity_y += cfg.GRAVITY
        else:
            self.velocity_y = 0

        self.x += self.velocity_x
        self.y += self.velocity_y

        # Синхронизируем rect после изменения координат
        self.rect.topleft = (int(self.x), int(self.y))

        # 3. Коллизии
        if platforms:
            self._check_collisions(platforms)

        # 4. Границы экрана
        self.x = max(0, min(self.x, cfg.SCREEN_WIDTH - self.width))
        self.rect.x = int(self.x)  # Синхронизируем X после границ

        # 5. Анимация
        if abs(self.velocity_x) > 0:
            self.current_animation = 'run'
        else:
            self.current_animation = 'idle'
        self.animations[self.current_animation].update()

    def _check_collisions(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                # Если кот падает или стоит на платформе
                if self.velocity_y >= 0:
                    self.y = plat.top - self.height
                    self.rect.y = int(self.y)  # Мгновенная синхронизация
                    self.velocity_y = 0
                    self.on_ground = True
                    break

    def jump(self):
        if self.on_ground:
            self.velocity_y = cfg.JUMP_POWER
            self.on_ground = False

    def draw(self, screen):
        frame = self.animations[self.current_animation].get_frame()
        if not frame:
            return

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        # ИСПРАВЛЕНИЕ: Рисуем только целые координаты
        screen.blit(frame, (int(self.x), int(self.y)))
