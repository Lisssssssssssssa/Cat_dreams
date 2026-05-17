import pygame


class Camera:
    """Камера для приближения/отдаления и перемещения по уровню."""

    def __init__(self, width, height):
        self.state = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.zoom = 1.0  # 1.0 = обычный масштаб, 2.0 = увеличение в 2 раза
        self.target_zoom = 1.0

    def apply(self, entity_rect):
        x = entity_rect.x - self.state.x
        y = entity_rect.y - self.state.y

        x = int(x * self.zoom)
        y = int(y * self.zoom)
        w = int(entity_rect.width * self.zoom)
        h = int(entity_rect.height * self.zoom)

        return pygame.Rect(x, y, w, h)

    def apply_pos(self, pos):
        x = (pos[0] - self.state.x) * self.zoom
        y = (pos[1] - self.state.y) * self.zoom
        return (int(x), int(y))

    def update(self, target_rect=None):
        if target_rect:
            # Центрируем на цели
            self.state.x = target_rect.centerx - self.width // 2
            self.state.y = target_rect.centery - self.height // 2

            # Ограничиваем границы экрана
            self.state.clamp_ip(pygame.Rect(0, 0, self.width, self.height))

        # Плавный зум
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * 0.1
        else:
            self.zoom = self.target_zoom

    def zoom_in(self):
        """Увеличить."""
        self.target_zoom = min(3.0, self.target_zoom + 0.5)

    def zoom_out(self):
        """Уменьшить."""
        self.target_zoom = max(0.5, self.target_zoom - 0.5)

    def reset_zoom(self):
        """Сбросить зум."""
        self.target_zoom = 1.0
        self.state = pygame.Rect(0, 0, self.width, self.height)
