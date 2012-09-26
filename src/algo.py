from collections import deque

def bfs(graph, src, dst, neighbours):
	"""Breadth-first search"""
	path = {src: None}
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

def read_path(path, dst):
	if dst not in path:
		return []
	result = []
	while dst:
		result.append(dst)
		dst = path[dst]
	return result

def shortest_path(graph, src, dst, neighbours):
	path = bfs(graph, src, dst, neighbours)
	return read_path(path, dst)

