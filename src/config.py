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

ICON_BORDER = 2
ICON_RADIUS = 9
ICON_FONTSIZE = 15
ICON_MARGIN = 2
ICON_PADDING = 4

COLOR_FONT = (0, 0, 0)
COLOR_BG = (159, 182, 205)
COLOR_BORDER = (50, 50, 50)
COLOR_SELECTED = (255,255,0)

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

RACE_SPRITES = {"Longear": ("sprite_collection.png", 1)
	,"Ghost": ("sprite_collection.png", 2)
	,"Croco": ("sprite_collection.png", 3)
	,"Human": ("chibi_races_V2_colorkey_fixed.png", 1)
	,"Human2": ("chibi_races_V2_colorkey_fixed.png", 2)
	,"Devil": ("chibi_races_V2_colorkey_fixed.png", 3)
	,"Human3": ("chibi_races_V2_colorkey_fixed.png", 4)
	,"Elf": ("chibi_races_V2_colorkey_fixed.png", 5)
	,"Alien": ("chibi_races_V2_colorkey_fixed.png", 6)
	,"WhiteGuy": ("chibi_races_V2_colorkey_fixed.png", 7)
	,"Medusa": ("chibi_races_V2_colorkey_fixed.png", 8)
	,"Dragon": ("chibi_races_V2_colorkey_fixed.png", 9)
	,"Taurus": ("chibi_races_V2_colorkey_fixed.png", 10)
	,"Squid": ("chibi_races_V2_colorkey_fixed.png", 11)
	,"GreyGuy": ("chibi_races_V2_colorkey_fixed.png", 12)
	,"Imhotep": ("chibi_races_V2_colorkey_fixed.png", 13)
	,"Wolf": ("chibi_races_V2_colorkey_fixed.png", 14)}

RACE_SPRITES = {"a": ("hair_collection_colorkey_fixed.png", 1)
	,"b": ("hair_collection_colorkey_fixed.png", 2)
	,"c": ("hair_collection_colorkey_fixed.png", 3)
	,"d": ("hair_collection_colorkey_fixed.png", 4)
	,"e": ("hair_collection_colorkey_fixed.png", 5)
	,"f": ("hair_collection_colorkey_fixed.png", 6)
	,"g": ("hair_collection_colorkey_fixed.png", 7)
	,"h": ("hair_collection_colorkey_fixed.png", 8)
	,"i": ("hair_collection_colorkey_fixed.png", 9)
	,"j": ("hair_collection_colorkey_fixed.png", 10)}

RACE_STATS = {"Longear": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Croco": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Human": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Human2": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Devil": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Human3": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Elf": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Alien": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"WhiteGuy": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Medusa": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Dragon": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Taurus": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Squid": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"GreyGuy": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Imhotep": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]
	,"Wolf": [("Health", 100), ("Defence", 80), ("Attack", 20), ("Dexterity", 40)]}
	
RACE_HAIRS = {"a": [("Human", 1), ("Human2", 0), ("Human3", 0)]
	,"b": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"c": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"d": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"e": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"f": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"g": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"h": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"i": [("Human", 0), ("Human2", 0), ("Human3", 0)]
	,"j": [("Human", 0), ("Human2", 0), ("Human3", 0)]}