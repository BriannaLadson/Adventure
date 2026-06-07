import os
import shutil
import shelve

#Data
def get_data(path, key):
	file = shelve.open(path)
	
	output = file[key]
	
	file.close()
	
	return output
	
def save_data(path, key, val):
	file = shelve.open(path)
	
	file[key] = val
	
	file.close()

#Dir & File
def create_dir(path):
	if not os.path.isdir(path):
		os.mkdir(path)
		
def overwrite_dir(path):
	if not os.path.isdir(path):
		os.mkdir(path)
		
	else:
		shutil.rmtree(path)
		
		os.mkdir(path)
		
#Misc.
def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
	hex_color = hex_color.lstrip("#")
	
	if len(hex_color) != 6:
		raise ValueError("Hex color must be in format RRGGBB")
		
	r = int(hex_color[0:2], 16)
	g = int(hex_color[2:4], 16)
	b = int(hex_color[4:6], 16)
	
	return (r,g,b)
	
def generate_shades(rgb, factor=0.7):
    r, g, b = rgb
    
    lighter = (
        min(int(r + (255 - r) * factor), 255),
        min(int(g + (255 - g) * factor), 255),
        min(int(b + (255 - b) * factor), 255)
    )
    
    original = (r, g, b)
    
    darker = (
        max(int(r * factor), 0),
        max(int(g * factor), 0),
        max(int(b * factor), 0)
    )
    
    return [lighter, original, darker]
	
def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
	
    return f"#{r:02x}{g:02x}{b:02x}"