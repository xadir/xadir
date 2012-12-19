from distutils.core import setup
import py2exe
import os

# PyGame thinks SDL_ttf.dll is a system dll, beat it to submission
# From: http://thadeusb.com/weblog/2009/4/15/pygame_font_and_py2exe
origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
       if os.path.basename(pathname).lower() in ["sdl_ttf.dll", "libogg-0.dll"]:
               return 0
       return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

basedir = '.'
data_dirs = 'gfx snd map font'.split()
data_files = []
for data_dir in data_dirs:
	filenames = os.listdir(data_dir)
	paths = []
	for filename in filenames:
		path = os.path.join(basedir, data_dir, filename)
		if os.path.isfile(path):
			paths.append(path)
	data_files.append((data_dir, paths))

setup(
		console=['runme.py'],
		packages=['src'],
		data_files=data_files
)
