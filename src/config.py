import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFXDIR = os.path.join(BASEDIR, 'gfx')
SNDDIR = os.path.join(BASEDIR, 'snd')
MAPDIR = os.path.join(BASEDIR, 'map')

SCALE = 2
ORIG_SIZE = 24
TARGET_SIZE = ORIG_SIZE * SCALE
ORIG_TILE_SIZE = (ORIG_SIZE, ORIG_SIZE)
TILE_SIZE = (TARGET_SIZE, TARGET_SIZE)
ORIG_CHAR_SIZE = (24, 32)
CHAR_SIZE = (SCALE * ORIG_CHAR_SIZE[0], SCALE * ORIG_CHAR_SIZE[1])
TILEGROUP_SIZE = (3 * TILE_SIZE[0], 3 * TILE_SIZE[1])

