import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASEDIR.endswith('.zip'): # Because py2exe, that's why (and deadlines)
	BASEDIR = os.path.dirname(BASEDIR)
GFXDIR = os.path.join(BASEDIR, 'gfx')
SNDDIR = os.path.join(BASEDIR, 'snd')
MAPDIR = os.path.join(BASEDIR, 'map')
FONTDIR = os.path.join(BASEDIR, 'font')

FONT = os.path.join(FONTDIR, 'FreeSansBold.ttf')
FONTSCALE = 0.6875

SCALE = 2
ORIG_SIZE = 24
TARGET_SIZE = ORIG_SIZE * SCALE
ORIG_TILE_SIZE = (ORIG_SIZE, ORIG_SIZE)
TILE_SIZE = (TARGET_SIZE, TARGET_SIZE)
ORIG_CHAR_SIZE = (24, 32)
CHAR_SIZE = (SCALE * ORIG_CHAR_SIZE[0], SCALE * ORIG_CHAR_SIZE[1])
TILEGROUP_SIZE = (3 * TILE_SIZE[0], 3 * TILE_SIZE[1])
ORIG_HAIR_SIZE = (22, 22)
HAIR_SIZE = (SCALE * ORIG_HAIR_SIZE[0], SCALE * ORIG_HAIR_SIZE[1])
