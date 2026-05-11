import random
import pygame
from collections import deque


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
        if self.room is None:
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

    def split_until_tasks(self, target_rooms, min_size = 80):
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
            if node.width > node.height:
                split_pos = random.randint(min_size, node.width - min_size)
                node.left = BSPNode(node.x, node.y, split_pos, node.height)
                node.right = BSPNode(node.x + split_pos, node.y, node.width - split_pos, node.height)
            else:
                split_pos = random.randint(min_size, node.height - min_size)
                node.left = BSPNode(node.x, node.y, node.width, split_pos)
                node.right = BSPNode(node.x, node.y + split_pos, node.width, node.height - split_pos)

            split(node.left)
            split(node.right)
        split(self)
        return rooms_list[:target_rooms]


def carve_corridor(grid, start, end):
    x1, y1 = start
    x2, y2 = end
    # L-shaped: horizontal then vertical
    for x in range(min(x1, x2), max(x1, x2) + 1):
        grid[y1][x] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        grid[y][x2] = 0
