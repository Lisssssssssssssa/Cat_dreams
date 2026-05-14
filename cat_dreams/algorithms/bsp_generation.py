import random
import pygame
from .bfs_validator import is_level_connected


class BSPNode:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = None
        self.right = None
        self.room = None  # (rx, ry, rw, rh)
        self.task_id = None
        self.connected_to = []

    def create_rooms(self, padding=10):
        if self.room is not None:
            return
        rw = self.width - padding * 2
        rh = self.height - padding * 2
        if rh < 20 or rw < 20:
            return
        rx = self.x + padding
        ry = self.y + padding
        self.room = (rx, ry, rw, rh)

    def get_room_center(self):
        if self.room:
            rx, ry, rw, rh = self.room
            return (rx + rw // 2, ry + rh // 2)
        if self.left:
            return self.left.get_room_center()
        if self.right:
            return self.right.get_room_center()
        return (self.x + self.width // 2, self.y + self.height // 2)

    def split_until_tasks(self, target_rooms, min_size=80):
        rooms_list = []

        def split(node):
            if len(rooms_list) >= target_rooms:
                node.create_rooms()
                if node.room:
                    rooms_list.append(node)
                return
            if len(rooms_list) == target_rooms - 1:
                node.create_rooms()
                if node.room:
                    rooms_list.append(node)
                return
            can_split_vertical = node.width >= min_size * 2 + 1
            can_split_horizontal = node.height >= min_size * 2 + 1

            if not can_split_vertical and not can_split_horizontal:
                # Не можем разделить ни в одном направлении → создаём комнату
                node.create_rooms()
                if node.room:
                    rooms_list.append(node)
                return

            # Выбираем направление деления
            if can_split_vertical and (not can_split_horizontal or node.width > node.height):
                # Вертикальный разрез (делим по ширине)
                max_split = node.width - min_size
                split_pos = random.randint(min_size, max_split)
                node.left = BSPNode(node.x, node.y, split_pos, node.height)
                node.right = BSPNode(node.x + split_pos, node.y, node.width - split_pos, node.height)
            else:
                # Горизонтальный разрез (делим по высоте)
                max_split = node.height - min_size
                split_pos = random.randint(min_size, max_split)
                node.left = BSPNode(node.x, node.y, node.width, split_pos)
                node.right = BSPNode(node.x, node.y + split_pos, node.width, node.height - split_pos)

            split(node.left)
            split(node.right)
        split(self)
        return rooms_list[:target_rooms]

    def assign_task(self, rooms):
        for i, node in enumerate(rooms):
            node.task_id = i
        return rooms

    def build_graph(self, rooms):
        corridors = []
        for i in range(len(rooms) - 1):
            room_a = rooms[i]
            room_b = rooms[i+1]
            room_a.connected_to.append(room_b.task_id)
            room_b.connected_to.append(room_a.task_id)
            center_a = room_a.get_room_center()
            center_b = room_b.get_room_center()

            x1, x2 = sorted([center_a[0], center_b[0]])
            y1 = center_a[1]
            h_corridor = pygame.Rect(x1, y1-10, x2-x1, 20)
            corridors.append(h_corridor)

            y1, y2 = sorted([center_a[1], center_b[1]])
            x2 = center_b[0]
            v_corridor = pygame.Rect(x2 - 10, y1, 20, y2 - y1)
            corridors.append(v_corridor)
        return corridors


def carve_corridor(grid, start, end, corridor_width):
    x1, y1 = start
    x2, y2 = end
    # L-shaped: horizontal then vertical
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= y1 < len(grid) and 0 <= x < len(grid[0]):
            for dy in range(-corridor_width // 2, corridor_width // 2 + 1):
                if 0 <= y1 + dy < len(grid):
                    grid[y1 + dy][x] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= y < len(grid) and 0 <= x2 < len(grid[0]):
            for dx in range(-corridor_width//2, corridor_width//2 + 1):
                if 0 <= x2 + dx < len(grid[0]):
                    grid[y][x2 + dx] = 0


def generate_level(width, height, num_tasks, min_room_size=80):
    root = BSPNode(0, 0, width, height)
    room_nodes = root.split_until_tasks(num_tasks, min_size=min_room_size)
    room_nodes = root.assign_task(room_nodes)
    corridors = root.build_graph(room_nodes)
    is_valid = is_level_connected(room_nodes)
    rooms = []
    for node in room_nodes:
        if node.room:
            rx, ry, rw, rh = node.room
            rooms.append({
                'rect': pygame.Rect(rx, ry, rw, rh),
                'task_id': node.task_id,
                'center': node.get_room_center(),
                'connected_to': node.connected_to
            })
    return {
        'rooms': rooms,
        'corridors': corridors,
        'is_valid': is_valid,
        'num_tasks': num_tasks
    }
