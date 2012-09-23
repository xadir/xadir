import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFXDIR = os.path.join(BASEDIR, 'gfx')
SNDDIR = os.path.join(BASEDIR, 'snd')
MAPDIR = os.path.join(BASEDIR, 'map')

SCALE = 3
ORIG_SIZE = 16
TARGET_SIZE = ORIG_SIZE * SCALE
ORIG_TILE_SIZE = (ORIG_SIZE, ORIG_SIZE)
TILE_SIZE = (TARGET_SIZE, TARGET_SIZE)
TILEGROUP_SIZE = (3 * TILE_SIZE[0], 3 * TILE_SIZE[1])

