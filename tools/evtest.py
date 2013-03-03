import pygame, time

pygame.init()
screen = pygame.display.set_mode((100, 100))

while True:
	for event in pygame.event.get():
		print event
		if event.type == pygame.QUIT:
			raise SystemExit

	time.sleep(0.05)

