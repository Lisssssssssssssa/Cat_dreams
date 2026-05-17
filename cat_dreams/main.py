import pygame
import config as cfg
from entities.cat import Cat
from entities.zoom import Camera
from algorithms.bsp_generation import generate_level


def main():
    pygame.init()

    # Полноэкранный режим
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Cat Dreams - Level Editor 💤")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # Генерация уровня
    print("Генерация уровня...")
    level_data = generate_level(
        width=cfg.SCREEN_WIDTH,
        height=cfg.SCREEN_HEIGHT,
        num_tasks=5,
        min_room_size=200
    )

    if not level_data['is_valid']:
        print("❌ Ошибка: Уровень несвязный!")
        return

    print(f"✅ Уровень сгенерирован! Комнат: {len(level_data['rooms'])}")

    # Камера
    camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)

    # Режимы: 'overview' / 'edit_room'
    game_mode = 'overview'
    selected_room = None

    # Кот (изначально в первой комнате)
    start_room = level_data['rooms'][0]['rect']
    cat = Cat(start_room.x + 50, start_room.y + 20)

    # Платформы
    platforms = []
    for room in level_data['rooms']:
        platforms.append(room['rect'])
    platforms.extend(level_data['corridors'])

    running = True
    while running:
        dt = clock.tick(cfg.FPS)

        # === ОБРАБОТКА СОБЫТИЙ ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_BACKSPACE:
                    # Вернуться к общему виду
                    if game_mode == 'edit_room':
                        game_mode = 'overview'
                        camera.reset_zoom()
                        selected_room = None
                        # Возвращаем кота в первую комнату
                        cat.x = start_room.x + 50
                        cat.y = start_room.y + 20

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if game_mode == 'overview':
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = (mouse_x / camera.zoom) + camera.state.x
                        world_y = (mouse_y / camera.zoom) + camera.state.y

                        for room in level_data['rooms']:
                            if room['rect'].collidepoint(world_x, world_y):
                                game_mode = 'edit_room'
                                selected_room = room

                                # === ДИНАМИЧЕСКИЙ ЗУМ ===
                                room_w = room['rect'].width
                                room_h = room['rect'].height

                                # Сколько раз комната помещается в экран по ширине/высоте
                                zoom_x = cfg.SCREEN_WIDTH / room_w
                                zoom_y = cfg.SCREEN_HEIGHT / room_h
                                base_zoom = min(zoom_x, zoom_y)

                                # Коэффициент отступа (0.85 = комната займёт ~85% экрана)
                                PADDING_FACTOR = 0.85
                                target_zoom = base_zoom * PADDING_FACTOR

                                # Ограничиваем зум разумными пределами
                                target_zoom = max(0.4, min(target_zoom, 5.0))

                                # Применяем мгновенно
                                camera.zoom = target_zoom
                                camera.target_zoom = target_zoom

                                # Центрируем камеру с учётом нового зума
                                camera.state.x = room['rect'].centerx - (cfg.SCREEN_WIDTH / 2) / target_zoom
                                camera.state.y = room['rect'].centery - (cfg.SCREEN_HEIGHT / 2) / target_zoom

                                # Спавним кота ВНУТРИ комнаты (по центру, на полу)
                                cat.x = room['rect'].centerx - (cat.width // 2)
                                cat.y = room['rect'].y + 50  # Ставим кота ближе к верху комнаты (внутри видимой зоны)
                                cat.velocity_x = 0
                                cat.velocity_y = 0
                                cat.on_ground = False
                                break

        # === ОБНОВЛЕНИЕ ===
        keys = pygame.key.get_pressed()

        if game_mode == 'overview':
            # Общий вид: камера показывает весь уровень
            camera.update()
            cat.update(keys, platforms)
        else:
            # Режим редактирования комнаты
            if selected_room:
                # Камера зафиксирована на комнате (не двигается)
                # Только кот двигается внутри комнаты
                cat.update(keys, [selected_room['rect']])

        # === ОТРИСОВКА ===
        screen.fill(cfg.BLACK)

        if game_mode == 'overview':
            # Рисуем коридоры
            for corridor in level_data['corridors']:
                cam_rect = camera.apply(corridor)
                pygame.draw.rect(screen, cfg.GREY, cam_rect)

            # Рисуем комнаты
            for room in level_data['rooms']:
                cam_rect = camera.apply(room['rect'])
                pygame.draw.rect(screen, cfg.BLUE, cam_rect, 2)

                # Текст с номером задачи
                text_pos = camera.apply_pos((room['rect'].x + 10, room['rect'].y + 10))
                text = font.render(f"Task {room['task_id']} (клик для редактирования)", True, cfg.WHITE)
                screen.blit(text, text_pos)

            # Рисуем кота (СПРАЙТ, а не квадрат!)
            cat.draw_with_camera(screen, camera)

            # Подсказка
            hint = font.render("ESC - выход | Клик по комнате - редактировать | BACKSPACE - назад", True, cfg.WHITE)
            screen.blit(hint, (10, cfg.SCREEN_HEIGHT - 30))

        else:
            # Режим редактирования комнаты
            if selected_room:
                # Рисуем комнату
                cam_rect = camera.apply(selected_room['rect'])
                pygame.draw.rect(screen, cfg.BLUE, cam_rect, 3)

                # Текст
                text_pos = camera.apply_pos((selected_room['rect'].x + 10, selected_room['rect'].y + 10))
                text = font.render(f"Task {selected_room['task_id']} (BACKSPACE - назад)", True, cfg.WHITE)
                screen.blit(text, text_pos)

                # Рисуем кота (СПРАЙТ, а не квадрат!)
                cat.draw_with_camera(screen, camera)

                # Подсказка
                hint = font.render("WASD - движение | Пробел - прыжок | BACKSPACE - назад", True, cfg.WHITE)
                screen.blit(hint, (10, cfg.SCREEN_HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()