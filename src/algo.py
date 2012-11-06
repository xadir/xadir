from collections import deque

def bfs(graph, src, dst, neighbours):
	"""Breadth-first search"""
	path = {src: None}
	if src == dst:
		return path
	seen = set([src])
	queue = deque([src])
	while queue:
		v = queue.popleft()
		for u in neighbours(graph, v):
			if u not in seen:
				path[u] = v
				if u == dst:
					return path
				seen.add(u)
				queue.append(u)
	return {}

def bfs_any(graph, src, dsts, neighbours):
	"""Breadth-first search, shortest path to any target"""
	path = {src: None}
	if src in dsts:
		return path, src
	seen = set([src])
	queue = deque([src])
	while queue:
		v = queue.popleft()
		for u in neighbours(graph, v):
			if u not in seen:
				path[u] = v
				if u in dsts:
					return path, u
				seen.add(u)
				queue.append(u)
	return {}, None

def bfs_area(graph, src, max_dist, neighbours):
	"""Reachable neighbours"""
	seen = set([src])
	queue = deque([(src, 0)]) if max_dist > 0 else None
	while queue:
		v, dist = queue.popleft()
		dist += 1
		for u in neighbours(graph, v):
			if u not in seen:
				seen.add(u)
				if dist < max_dist:
					queue.append((u, dist))
	return seen

def read_path(path, dst):
	if dst not in path:
		return []
	result = []
	while dst:
		result.append(dst)
		dst = path[dst]
	result.reverse()
	return result

def shortest_path(graph, src, dst, neighbours):
	path = bfs(graph, src, dst, neighbours)
	return read_path(path, dst)

def shortest_path_any(graph, src, dsts, neighbours):
	path, dst = bfs_any(graph, src, dsts, neighbours)
	return read_path(path, dst)

