import pygame
import config as cfg
from entities.cat import Cat
from algorithms.bsp_generation import generate_level


def main():
    pygame.init()
    # Создание окна
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat Dreams 💤")
    clock = pygame.time.Clock()
    level_data = generate_level(
        width=cfg.SCREEN_WIDTH,
        height=cfg.SCREEN_HEIGHT,
        num_tasks=3,
        min_room_size=100
        )
    if not level_data['is_valid']:
        print('ошибка')
        return
    print('уровень создан')
    platforms = []
    for room in level_data['rooms']:
        platforms.append(room['rect'])
    # Добавляем коридоры как платформы
    platforms.extend(level_data['corridors'])

    # 3. Создание кота (спавним в первой комнате)
    start_room = level_data['rooms'][0]['rect']
    # Ставим кота чуть выше пола первой комнаты
    cat = Cat(start_room.x + 50, start_room.y + 20)

    running = True
    while running:
        dt = clock.tick(cfg.FPS)  # Ограничиваем до 60 FPS

        # 1.обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Получаем состояние клавиш
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            cat.jump()

        # 2. обновление
        cat.update(keys, platforms)
        # 3. отрисовка
        screen.fill(cfg.BLACK)
        for corridor in level_data['corridors']:
            pygame.draw.rect(screen, cfg.GREY, corridor)

        # Рисуем рамки комнат (синим цветом) и ID задач
        font = pygame.font.SysFont("Arial", 14)
        for room in level_data['rooms']:
            # Рамка комнаты
            pygame.draw.rect(screen, cfg.BLUE, room['rect'], 2)

            # Текст с номером задачи
            text = font.render(f"Task {room['task_id']}", True, cfg.WHITE)
            screen.blit(text, (room['rect'].x + 10, room['rect'].y + 10))
        cat.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
