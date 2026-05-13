from collections import deque


def is_level_connected(rooms):
    if not rooms:
        return False

    start_node_id = 0
    visited = set([start_node_id])
    queue = deque([start_node_id])
    while queue:
        current_id = queue.popleft()
        for room in rooms:
            if room.task_id == current_id:
                for neighbor_id in room.connected_to:
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)
                break
    return len(visited) == len(rooms)
