#! /usr/bin/env python
import Image
import sys

class Item(set):
	pass

im = Image.open(sys.argv[1])

pixels = im.load()

queued = set()
queue = set([(0, 0)])
color = pixels[0, 0]

background = set()

while queue:
	p = x, y = queue.pop()
	if pixels[p] != color:
		continue
	background.add(p)

	for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
		p = x + dx, y + dy
		if p[0] < 0 or p[0] >= im.size[0] or p[1] < 0 or p[1] >= im.size[1]:
			continue
		if p not in queued:
			queue.add(p)
			queued.add(p)

del queued, queue

foreground = set((x, y) for y in range(im.size[1]) for x in range(im.size[0])) - background

del background

items = []

while foreground:
	item = set()
	queue = set([foreground.pop()])

	while queue:
		p = x, y = queue.pop()
		item.add(p)

		for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
			p = x + dx, y + dy
			if p in foreground:
				foreground.remove(p)
				queue.add(p)

	item = Item(item)
	item.xset = set(x for x, y in item)
	item.yset = set(y for x, y in item)
	item.minx = min(item.xset)
	item.miny = min(item.yset)
	item.maxx = max(item.xset)
	item.maxy = max(item.yset)
	item.width = item.maxx - item.minx
	item.height = item.maxy - item.miny

	items.append(item)

rows = []
while items:
	# Find topmost point
	top = None
	for item in items:
		if top is None or item.miny < top:
			top = item.miny

	# Find top left item
	mdist = None
	sitem = None
	for item in items:
		dist = item.minx ** 2 + (item.miny - top) ** 2
		if mdist is None or dist < mdist:
			mdist = dist
			sitem = item

	# Find non-colliding items
	collide = set()
	sitems = []
	while sitem:
		#print sitem.minx, sitem.miny, '        |', sitem.maxx, sitem.maxy
		collide |= sitem.xset
		sitems.append(sitem)
		items.remove(sitem)

		mdist = None
		sitem = None
		for item in items:
			if item.xset & collide:
				continue
			if item.xset & set(x for xitem in items for x in xitem.xset if xitem.maxy < item.miny):
				continue
			if not item.yset & set(y for xitem in sitems for y in xitem.yset):
				continue
			if item.minx < max(xitem.maxx for xitem in sitems):
				continue
			dist = item.minx ** 2 + (item.miny - top) ** 2
			if mdist is None or dist < mdist:
				mdist = dist
				sitem = item
	#print

	rows.append(sitems)

#print len(rows)
#print [len(row) for row in rows]

#for row in rows:
#	for item in row:
#		print (item.minx, item.miny),
#	print

import ImageDraw

out = Image.new('RGB', (max(map(len, rows))*24, len(rows)*24))
draw=ImageDraw.Draw(out)
draw.rectangle((0, 0, out.size[0], out.size[1]), fill=(255, 255, 255))
for y, row in enumerate(rows):
	for x, item in enumerate(row):
		sub = im.crop((item.minx, item.miny, item.maxx+1, item.maxy+1))
		yoff = 24 - (item.maxy - item.miny + 1)
		xoff = (24 - (item.maxx - item.minx)) / 2
		out.paste(sub, (x*24 + xoff, y*24 + yoff))

out.save('aligned.png')

