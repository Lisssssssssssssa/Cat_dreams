import pygame
import config as cfg
from entities.cat import Cat


def main():
    pygame.init()
    # Создание окна
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat Dreams 💤")
    clock = pygame.time.Clock()
    # Создание кота
    cat = Cat(100, 400)
    # Пол
    floor = pygame.Rect(0, cfg.SCREEN_HEIGHT - 50, cfg.SCREEN_WIDTH, 50)
    platforms = [floor]
    running = True
    while running:
        # 1.обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Получаем состояние клавиш
        keys = pygame.key.get_pressed()
        # 2. обновление
        cat.update(keys, platforms)
        # 3. отрисовка
        screen.fill(cfg.BLACK)
        for platform in platforms:
            pygame.draw.rect(screen, cfg.GREY, platform)
        cat.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
