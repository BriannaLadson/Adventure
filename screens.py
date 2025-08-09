from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
import os
import random
from terraforgepro import TerraForgePro
import threading

import helpfunctions as helpf
import entities
import parsing
import commands

#Screens
class Screen(ttk.Frame):
	def __init__(self, root):
		super().__init__(root)
		
		self.root = root
		
class StartScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		#Title
		lbl = ttk.Label(self, text="Adventure")
		lbl.pack()
		
		#Options
		fr = ttk.Frame(self)
		fr.pack(pady=10)
		
		new_game_btn = ttk.Button(fr, text="New Game", command=lambda:EnterSaveNamePopup(root))
		new_game_btn.pack(side=LEFT)
		
		load_game_btn = ttk.Button(fr, text="Load Game")
		load_game_btn.pack(side=LEFT, padx=10)
		
		exit_btn = ttk.Button(fr, text="Exit", command=root.destroy)
		exit_btn.pack()
		
class ContentScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		#Title
		lbl = ttk.Label(self, text="Content", anchor="center")
		lbl.grid(row=0, column=0, sticky="we", columnspan=2)
		
		#Content
		self.content_var = StringVar()
		self.content_var.trace_add("write", self.trace)
		
		self.scr_fr = ScrollableFr(self)
		self.scr_fr.grid(row=1, column=0, sticky="nsew", columnspan=2)
		
		back_btn = ttk.Button(self, text="Back", command=self.back)
		back_btn.grid(row=2, column=0, sticky="we")
		
		self.continue_btn = ttk.Button(self, text="Continue", state="disabled", command=self.continue_)
		self.continue_btn.grid(row=2, column=1, sticky="we")
		
		self.load_content()
		
	def trace(self, *args):
		if len(self.content_var.get()) == 0:
			self.continue_btn.config(state="disabled")
			
		else:
			self.continue_btn.config(state="normal")
		
	def back(self):
		root = self.root
		
		root.start_screen = StartScreen(root)
		root.start_screen.pack(fill=BOTH, expand=1)
	
		self.destroy()
		
	def continue_(self):
		root = self.root
		
		content_path = "content/" + self.content_var.get()
		
		game = root.game = entities.Game(root.save_path, content_path)
		
		parsing.parse_xml(game)
		
		root.world_generation_screen = WorldGenerationScreen(root)
		root.world_generation_screen.pack(fill=BOTH, expand=1)
	
		self.destroy()
		
	def load_content(self):
		root = self.root
		
		content_packs = [d for d in os.listdir("content") if os.path.isdir(os.path.join("content", d))]
	
		if content_packs:
			self.content_var.set(content_packs[0])
			
		for index, pack in enumerate(content_packs):
			self.scr_fr.fr1.grid_columnconfigure(index, weight=1)
			
			rb = ttk.Radiobutton(
				self.scr_fr.fr1,
				text=pack,
				variable=self.content_var,
				value=pack,
			)
			
			rb.pack()
		
class WorldGenerationScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		game = self.game = root.game
		
		#Title
		title_lbl = ttk.Label(self, text="World Generation", anchor="center")
		title_lbl.pack(fill=X)
		
		#Middle
		middle_fr = ttk.Frame(self)
		middle_fr.pack(fill=BOTH, expand=1)
		
		#Middle - Settings
		settings_fr = ttk.Frame(middle_fr)
		settings_fr.pack(side=LEFT, fill=Y)
		
		self.notebook = ttk.Notebook(settings_fr)
		self.notebook.pack(fill=BOTH, expand=1)
		
		self.generate_btn = ttk.Button(settings_fr, text="Generate", command=self.start_generate)
		self.generate_btn.pack(fill=X)
		
		#Middle - Map
		map_fr = ttk.Frame(middle_fr)
		map_fr.pack(fill=BOTH, expand=1)
		
		self.filter_var = StringVar()
		self.filter_var.trace_add("write", self.trace_filter)
		
		self.filter_cbx = ttk.Combobox(map_fr, textvariable=self.filter_var)
		self.filter_cbx.pack()
		
		self.map_can = Canvas(map_fr)
		self.map_can.pack(fill=BOTH, expand=1)
		
		self.load_overworld_tab()
		self.load_region_tab()
		
		#Buttons
		btn_fr = ttk.Frame(self)
		btn_fr.pack()
		
		back_btn = ttk.Button(btn_fr, text="Back", command=self.back)
		back_btn.pack(side=LEFT, fill=X)
		
		self.continue_btn = ttk.Button(btn_fr, text="Continue", state="disabled", command=self.continue_)
		self.continue_btn.pack(side=LEFT, fill=X)
		
	def load_overworld_tab(self):
		#Overworld Tab / Notebook
		fr = ttk.Frame()
		
		self.overworld_notebook = ttk.Notebook(fr)
		self.overworld_notebook.pack(fill=BOTH, expand=1)
		
		self.notebook.add(fr, text="Overworld")
		
		#Sub Tabs
		self.load_general_tab()
		self.load_noise_types()
		self.load_key()
		
	def load_general_tab(self):
		fr = ttk.Frame()
		
		#Map Size
		map_size_lbl = ttk.Label(fr, text="Map Size")
		map_size_lbl.grid(row=0, column=0)
		
		self.map_size_var = IntVar(value=300)
		#self.map_size_var.trace_add("write", self.trace)
		
		map_size_ent = ttk.Entry(fr, textvariable=self.map_size_var)
		map_size_ent.grid(row=0, column=1)
		
		#Number of Islands
		island_num_lbl = ttk.Label(fr, text="Number of Islands")
		island_num_lbl.grid(row=1, column=0)
		
		self.island_num_var = IntVar(value=1)
		#self.island_num_var.trace_add("write", self.trace)
		
		island_num_ent = ttk.Entry(fr, textvariable=self.island_num_var)
		island_num_ent.grid(row=1, column=1)
		
		#Island Spread
		island_spread_lbl = ttk.Label(fr, text="Island Spread")
		island_spread_lbl.grid(row=2, column=0)
		
		self.island_spread_var = DoubleVar(value=.3)
		
		island_spread_ent = ttk.Entry(fr, textvariable=self.island_spread_var)
		island_spread_ent.grid(row=2, column=1)
		
		#Min Island Spread
		min_island_spacing_lbl = ttk.Label(fr, text="Minimum Island Spacing")
		min_island_spacing_lbl.grid(row=3, column=0)
		
		self.min_island_spacing_var = IntVar(value=0)
		
		min_island_spacing_ent = ttk.Entry(fr, textvariable=self.min_island_spacing_var)
		min_island_spacing_ent.grid(row=3, column=1)
		
		self.overworld_notebook.add(fr, text="General")
		
	def load_region_tab(self):
		#Region Tab/Notebook
		fr = ttk.Frame(self.notebook)
		
		self.region_notebook = ttk.Notebook(fr)
		self.region_notebook.pack(fill=BOTH, expand=1)
		
		self.notebook.add(fr, text="Region")
		
		self.load_region_general_tab()
		self.load_region_noise_types()
		
	def load_noise_types(self):
		game = self.game
		
		filters = ["Biome",]
		
		for noise_type in game.noise_types:
			tab = NoiseTypeTab(self.overworld_notebook, noise_type)
			
			self.overworld_notebook.add(tab, text=noise_type.name)
			
			filters.append(noise_type.name)
			
		self.filter_cbx["values"] = filters
		
	def load_key(self):
		game = self.game
		
		fr = ttk.Frame(self.overworld_notebook)
		
		row = 0
		
		for biome in game.biomes:
			lbl = ttk.Label(fr, text=biome.name)
			lbl.grid(row=row, column=0)
			
			lbl1 = Label(fr, bg=biome.color, text="     ")
			lbl1.grid(row=row, column=1, sticky="we")
			
			row += 1
			
		self.overworld_notebook.add(fr, text="Biomes")
			
	def load_region_general_tab(self):
		game = self.game
		
		fr = ttk.Frame()
		
		#Region Size
		region_size_lbl = ttk.Label(fr, text="Region Size")
		region_size_lbl.grid(row=0, column=0)
		
		self.region_size_var = IntVar(value=32)
		
		region_size_ent = ttk.Entry(fr, textvariable=self.region_size_var)
		region_size_ent.grid(row=0, column=1)
		
		#Number of Islands
		region_island_num_lbl = ttk.Label(fr, text="Number of Islands")
		region_island_num_lbl.grid(row=1, column=0)
		
		self.region_island_num_var = IntVar(value=1)
		
		region_island_num_ent = ttk.Entry(fr, textvariable=self.region_island_num_var)
		region_island_num_ent.grid(row=1, column=1)
		
		#Island Spread
		region_island_spread_lbl = ttk.Label(fr, text="Island Spread")
		region_island_spread_lbl.grid(row=2, column=0)
		
		self.region_island_spread_var = DoubleVar(value=.3)
		
		self.region_island_spread_ent = ttk.Entry(fr, textvariable=self.region_island_spread_var)
		self.region_island_spread_ent.grid(row=2, column=1)
		
		#Min Island Spread
		region_min_island_spacing_lbl = ttk.Label(fr, text="Minimum Island Spacing")
		region_min_island_spacing_lbl.grid(row=3, column=0)
		
		self.region_min_island_spacing_var = IntVar(value=0)
		
		region_min_island_spacing_ent = ttk.Entry(fr, textvariable=self.region_min_island_spacing_var)
		region_min_island_spacing_ent.grid(row=3, column=1)
		
		self.region_notebook.add(fr, text="General")
		
	def load_region_noise_types(self):
		game = self.game
		
		for noise_type in game.region_noise_types:
			tab = NoiseTypeTab(self.region_notebook, noise_type)
			
			self.region_notebook.add(tab, text=noise_type.name)

			
	def start_generate(self):
		self.generate_btn.config(state="disabled")
		
		threading.Thread(target=self.generate).start()
			
	def generate(self):
		root = self.root
		game = self.game
		
		#Popup
		popup = GeneratePopup(root)
		popup.center()
		
		#Noise Types
		noise_types = {}
		
		for noise_type in game.noise_types:
			noise_types[noise_type.id] = noise_type.convert_to_dict()	
			
		#Biomes
		biomes = []
		
		for biome in game.biomes:
			biomes.append(biome.convert_to_dict())
			
		self.map_can.update_idletasks()
		width = self.map_can.winfo_width()
		height = self.map_can.winfo_height()
		
		#Overworld Generator
		self.generator = TerraForgePro(
			noise_types=noise_types,
			biomes=biomes,
			map_size=self.map_size_var.get(),
			image_size=(width, height),
			num_islands=self.island_num_var.get(),
			island_spread=self.island_spread_var.get(),
		)
		self.generator.generate(output_dir=game.save_path)
		
		#Region Overworld
		region_noise_types = {}
		
		for noise_type in game.region_noise_types:
			region_noise_types[noise_type.id] = noise_type.convert_to_dict()
		
		self.region_generator = TerraForgePro(
			noise_types=region_noise_types,
			
		)
		
		popup.destroy()
		
		self.filter_var.set("Biome")
		
		self.generate_btn.config(state="normal")
		self.continue_btn.config(state="normal")
		
		
		
	def trace_filter(self, *args):
		game = self.game
		
		img_path = f"{game.save_path}/{self.filter_var.get().lower()}_map.png"
		
		self.filter_img = PhotoImage(file=img_path)
		
		self.map_can.delete("all")
		
		self.map_can.create_image(0, 0, anchor="nw", image=self.filter_img)
		
	def trace(self, *args):
		state = "normal"
		
		int_vars = {
			"map_size" : 1,
			"island_num": 1,
		}
		
		for key in int_vars:
			val = getattr(self, key + "_var").get()
			min = int_vars[key]
			
			try:
				if val < min:
					raise ValueError
			
			except:
				state="disabled"
		
		self.generate_btn.config(state=state)
		
	def back(self):
		root = self.root
		
		root.start_screen = StartScreen(root)
		root.start_screen.pack(fill=BOTH, expand=1)
	
		self.destroy()
		
	def continue_(self):
		root = self.root
		game = self.game
		
		game.world_settings = {
			"map_size": self.map_size_var.get(),
			"num_islands": self.island_num_var.get(),
			"island_spread": self.island_spread_var.get(),
			"min_island_spacing": self.min_island_spacing_var.get(),
			"noise_types": self.generator.noise_types,
			"biomes": self.generator.biomes,
			"region_size": self.region_size_var.get(),
			"region_num_islands": self.region_island_num_var.get(),
			"region_island_spread": self.region_island_spread_var.get(),
			"region_min_island_spacing": self.min_island_spacing_var.get(),
			"region_noise_types": self.region_generator.noise_types,
		}
		
		root.character_creation_screen = CharacterCreationScreen(root)
		root.character_creation_screen.pack(fill=BOTH, expand=1)
	
		self.destroy()

class CharacterCreationScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		
		title_lbl = ttk.Label(self, text="Character Creation", anchor="center",)
		title_lbl.grid(row=0, column=0, sticky="nsew", columnspan=2)
		
		back_btn = ttk.Button(self, text="Back", command=self.back)
		back_btn.grid(row=2, column=0, sticky="ew")
		
		self.continue_btn = ttk.Button(self, text="Continue", command=self.continue_)
		self.continue_btn.grid(row=2, column=1, sticky="we")
		
	def back(self):
		root = self.root
		
		root.world_generation_screen = WorldGenerationScreen(root)
		root.world_generation_screen.pack(fill=BOTH, expand=1)
	
		self.destroy()
		
	def continue_(self):
		root = self.root
		game = root.game
		
		player = game.player = entities.Player()
		
		game.random_region_placement(player)
		
		helpf.save_data(game.save_path + "/game_data", "game", game)
		
		root.play_screen = PlayScreen(root)
		root.play_screen.pack(fill=BOTH, expand=1)
		
		self.destroy()
		
class PlayScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		game = self.game = helpf.get_data(root.save_path + "/game_data", "game")
		player = self.player = game.player
		
		terra = game.terra = TerraForgePro(
			noise_types = game.world_settings["noise_types"],
			biomes = game.world_settings["biomes"],
			map_size = game.world_settings["map_size"],
			num_islands = game.world_settings["num_islands"],
			island_spread = game.world_settings["island_spread"],
			min_island_spacing = game.world_settings["min_island_spacing"],
		)
		terra.generate_noise()
		terra.assign_biomes()
		self.fast_travel_can = None
		self.local_map_can = None
		
		#Location
		self.location_var = StringVar(value=player.get_location())
		
		location_lbl = ttk.Label(self, textvariable=self.location_var)
		location_lbl.pack(fill=X)
		
		if player.lx is None:
			self.fast_travel_can = FastTravelCanvas(self, game)
			self.fast_travel_can.pack(fill=BOTH, expand=1)
			self.fast_travel_can.update_idletasks()
			
		else:
			self.local_map_can = LocalMapCanvas(self, game)
			self.local_map_can.pack(fill=BOTH, expand=1)
			self.local_map_can.update_idletasks()
		
		self.update_screen()
		
		root.bind("<Up>", lambda e: commands.process_cmd(e, self, "north"))
		root.bind("<Down>", lambda e: commands.process_cmd(e, self, "south"))
		root.bind("<Left>", lambda e: commands.process_cmd(e, self, "west"))
		root.bind("<Right>", lambda e: commands.process_cmd(e, self, "east"))
		
		root.bind("8", lambda e: commands.process_cmd(e, self, "north"))
		root.bind("7", lambda e: commands.process_cmd(e, self, "northwest"))
		root.bind("9", lambda e: commands.process_cmd(e, self, "northeast"))
		
		root.bind("2", lambda e: commands.process_cmd(e, self, "south"))
		root.bind("1", lambda e: commands.process_cmd(e, self, "southwest"))
		root.bind("3", lambda e: commands.process_cmd(e, self, "southeast"))
		
		root.bind("4", lambda e: commands.process_cmd(e, self, "west"))
		root.bind("6", lambda e: commands.process_cmd(e, self, "east"))
		
		root.bind("5", lambda e: commands.process_cmd(e, self, "in"))
		
	def update_screen(self):
		player = self.player
		
		self.location_var.set(player.get_location())
		
		if player.lx is None:
			self.remove_local_map()
			
			self.create_fast_travel_map()
			
		else:
			self.remove_fast_travel_map()
			
			self.create_local_map()
			
	def create_fast_travel_map(self):
		if self.fast_travel_can is None:
			self.fast_travel_can = FastTravelCanvas(self, self.game)
			self.fast_travel_can.pack(fill=BOTH, expand=1)
			
		else:
			self.fast_travel_can.draw_map()
			
	def remove_fast_travel_map(self):
		if self.fast_travel_can is not None:
			self.fast_travel_can.destroy()
			self.fast_travel_can = None
			
	def create_local_map(self):
		player = self.player
		
		if self.local_map_can is None:
			self.local_map_can = LocalMapCanvas(self, self.game)
			self.local_map_can.pack(fill=BOTH, expand=1)
			
		else:
			self.local_map_can.draw_map()
			
	def remove_local_map(self):
		if self.local_map_can is not None:
			self.local_map_can.destroy()
			self.local_map_can = None
		
#Popups
class Popup(Toplevel):
	def __init__(self, root):
		super().__init__(root)
		
		self.root = root
		
		self.overrideredirect(True)
		
		self.grab_set()
	
	def center(self):
		self.update_idletasks()
		
		sw = self.winfo_screenwidth()
		sh = self.winfo_screenheight()
		
		tw = self.winfo_width()
		th = self.winfo_height()
		
		x = (sw // 2) - (tw // 2)
		y = (sh // 2) - (th // 2)
		
		self.geometry(f"{tw}x{th}+{x}+{y}")
		
class EnterSaveNamePopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		self.var = StringVar()
		self.var.trace_add("write", self.trace)
		
		ent = ttk.Entry(self, textvariable=self.var)
		ent.grid(row=0, column=0, columnspan=2, sticky="we")
		
		back_btn = ttk.Button(self, text="Back", command=self.destroy)
		back_btn.grid(row=1, column=0)
		
		self.continue_btn = ttk.Button(self, text="Continue", state="disabled", command=self.continue_)
		self.continue_btn.grid(row=1, column=1)
		
		self.center()
		
		self.trace()
		
	def trace(self, *args):
		if len(self.var.get()) == 0:
			self.continue_btn.config(state="disabled")
			
		else:
			self.continue_btn.config(state="normal")
			
	def continue_(self):
		root = self.root
		
		root.save_path = "saves/" + self.var.get()
		
		if not os.path.isdir(root.save_path):
			os.mkdir(root.save_path)
			
			root.start_screen.destroy()
			
			root.content_screen = ContentScreen(root)
			root.content_screen.pack(fill=BOTH, expand=1)
			
		else:
			popup = OverwriteSavePopup(root)
			popup.center()
			
		self.destroy()
	
class GeneratePopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		ttk.Label(self, text="Generating World...").pack()
		
		self.center()
	
class OverwriteSavePopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		self.grid_rowconfigure(2, weight=1)
		
		lbl = ttk.Label(self, text="Do you want to overwrite the following save?")
		lbl.grid(row=0, column=0, columnspan=2)
		
		lbl1 = ttk.Label(self, text=root.save_path)
		lbl1.grid(row=1, column=0, columnspan=2)
		
		yes_btn = ttk.Button(self, text="Yes", command=lambda: self.continue_(True))
		yes_btn.grid(row=2, column=0, sticky="we")
		
		no_btn = ttk.Button(self, text="No", command=lambda: self.continue_(False))
		no_btn.grid(row=2, column=1, sticky="we")
		
		self.center()
		
	def continue_(self, bool):
		root = self.root
		
		if not bool:
			popup = EnterSaveNamePopup(root)
			popup.center()
			
		else:
			helpf.overwrite_dir(root.save_path)
			
			root.start_screen.destroy()
			
			root.content_screen = ContentScreen(root)
			root.content_screen.pack(fill=BOTH, expand=1)
			
		self.destroy()
		
#Widgets
class FastTravelCanvas(Canvas):
	def __init__(self, parent, game):
		super().__init__(parent, bg="lightblue")
		
		self.game = game
		player = self.player = game.player
		
		self.tile_num = 25
		self.min_tiles = 11
		self.max_tiles = 51
		
		self.bind("<Configure>", self.draw_map)
		
		self.bind("<MouseWheel>", self.on_mousewheel)
		
	def draw_map(self, event=None):
		game = self.game
		terra = game.terra
		player = self.player
		
		self.update_idletasks()
		
		width = self.winfo_width()
		height = self.winfo_height()
		
		#tile_size = min(width // self.tile_num, height // self.tile_num)
		
		tile_width = width / self.tile_num
		tile_height = height / self.tile_num
		
		half = self.tile_num // 2
		
		self.delete("map")
		
		#pad_x = (width - tile_size * self.tile_num) // 2
		#pad_y = (height - tile_size * self.tile_num) // 2
		
		for row in range(self.tile_num):
			for col in range(self.tile_num):
				region_x = player.gx - half + col
				region_y = player.gy - half + row
				
				color = terra.tile_color(region_x, region_y)
				
				x0 = col * tile_width
				y0 = row * tile_height
				
				x1 = x0 + tile_width
				y1 = y0 + tile_height
				
				self.create_rectangle(
					x0, y0,
					x1, y1,
					fill=color,
					outline="",
					tags="map",
				)
				
		ctx = half * tile_width
		cty = half * tile_height
		
		ctx1 = ctx + tile_width
		cty1 = cty + tile_height
		
		cx = (ctx + ctx1) / 2
		cy = (cty + cty1) / 2
		radius = min(tile_width, tile_height) * .35
				
		self.create_oval(
			cx - radius, cy - radius,
			cx + radius, cy + radius,
			fill="red",
			outline="",
			tags="map",
		)
				
	def on_mousewheel(self, event):
		if event.delta > 0 or getattr(event, "num", None) == 4:
			if self.tile_num > self.min_tiles:
				self.tile_num -= 2
				
		else:
			if self.tile_num < self.max_tiles:
				self.tile_num += 2
					
		self.draw_map()
		
class LocalMapCanvas(Canvas):
	def __init__(self, parent, game):
		super().__init__(parent, bg="lightblue")
		
		self.root = parent.master
		self.game = game
		player = self.player = game.player
		
		self.region_map = None
		
		self.tile_num = 25
		self.min_tiles = 11
		self.max_tiles = 51
		
		self.structures_map = []
		map_size = game.world_settings["region_size"]
		for y in range(map_size):
			y_array = []
			
			for x in range(map_size):
				y_array.append(None)
				
			self.structures_map.append(y_array)
		
		threading.Thread(target=self.generate).start()
		
	def generate(self):
		game = self.game
		player = self.player
		
		world_size = game.world_settings["map_size"]
		
		self.seed = player.gy * world_size + player.gx + 1
		
		popup = GeneratePopup(self.root)
		popup.center()
		
		self.generate_terrain()
		self.generate_ore()
		
		popup.destroy()
		
		self.bind("<Configure>", self.draw_map)
		self.draw_map()
		
	def generate_terrain(self):
		game = self.game
		player = self.player
		
		region_color = game.terra.tile_color(player.gx, player.gy)
		region_biome = helpf.get_obj_by_attr_val(game.biomes, "color", region_color)
		
		noise_types = game.world_settings["region_noise_types"]
		for noise_type in noise_types.values():
			world_size = game.world_settings["map_size"]
			noise_type["seed"] = self.seed
		
		self.region_terra = TerraForgePro(
			noise_types = game.world_settings["region_noise_types"],
			map_size = game.world_settings["region_size"],
			num_islands = game.world_settings["region_num_islands"],
			island_spread = game.world_settings["region_island_spread"],
			min_island_spacing = game.world_settings["region_min_island_spacing"],
			biomes = region_biome.tile_types,
		)
		
		self.region_terra.generate_noise()
		
	def generate_ore(self):
		game = self.game
		player = self.player
		
		rng = random.Random(self.seed)
		
		ore_deposit = rng.choice(game.ore_deposits)
		
		map_size = game.world_settings["region_size"]
		
		deposit_x = rng.randint(0, map_size - 1)
		deposit_y = rng.randint(0, map_size - 1)
		
		ore_deposit_structure = entities.OreDepositStructure(
			player.gx,
			player.gy,
			deposit_x,
			deposit_y,
			0,
			ore_deposit,
		)
		
		self.structures_map[deposit_y][deposit_x] = ore_deposit_structure
		
	def draw_map(self, event=None):
		game = self.game
		player = self.player
		
		self.update_idletasks()
		
		width = self.winfo_width()
		height = self.winfo_height()
		
		tile_width = width / self.tile_num
		tile_height = height / self.tile_num
		
		half = self.tile_num // 2
		
		region_size = self.region_terra.map_size
		
		self.delete("map")
		
		for row in range(self.tile_num):
			for col in range(self.tile_num):
				local_x = player.lx - half + col
				local_y = player.ly - half + row
				
				if 0 <= local_x < region_size and 0 <= local_y < region_size:
					color = self.region_terra.tile_color(local_x, local_y)
					
				else:
					color = "black"
				
				x0 = col * tile_width
				y0 = row * tile_height
				
				x1 = x0 + tile_width
				y1 = y0 + tile_height
				
				tile = self.create_rectangle(
					x0, y0,
					x1, y1,
					fill=color,
					outline="black",
					tags="map",
				)
				
				#Draw Structure
				h = len(self.structures_map)
				w = len(self.structures_map[0]) if h else 0
				
				if 0 <= local_x < w and 0 <= local_y < h:
					structure = self.structures_map[local_y][local_x]
				
					if not structure == None:
						structure.draw(self, tile)
				
		ctx = half * tile_width
		cty = half * tile_height
		
		ctx1 = ctx + tile_width
		cty1 = cty + tile_height
		
		cx = (ctx + ctx1) / 2
		cy = (cty + cty1) / 2
		
		radius = min(tile_width, tile_height) * .35
		
		self.create_oval(
			cx - radius, cy - radius,
			cx + radius, cy + radius,
			fill="red",
			outline="",
			tags="map",
		)

class NoiseTypeTab(ttk.Frame):
	def __init__(self, parent, noise_type):
		super().__init__(parent)
		
		self.noise_type = noise_type
		
		#Seed
		seed_lbl = ttk.Label(self, text="Seed:")
		seed_lbl.grid(row=0, column=0)
		
		self.seed_var = IntVar(value=noise_type.seed)
		self.seed_var.trace_add("write", self.trace)
		
		seed_ent = ttk.Entry(self, textvariable=self.seed_var)
		seed_ent.grid(row=0, column=1)
		
		seed_btn = ttk.Button(self, text="?", command=self.random_seed)
		seed_btn.grid(row=0, column=2)
		
		#Octaves
		octaves_lbl = ttk.Label(self, text="Octaves:")
		octaves_lbl.grid(row=1, column=0)
		
		self.octaves_var = IntVar(value=noise_type.octaves)
		self.octaves_var.trace_add("write", self.trace)
		
		octaves_ent = ttk.Entry(self, textvariable=self.octaves_var)
		octaves_ent.grid(row=1, column=1)
		
		octaves_btn = ttk.Button(self, text="?", command=self.random_octaves)
		octaves_btn.grid(row=1, column=2)
		
		#Persistence
		persistence_lbl = ttk.Label(self, text="Persistence:")
		persistence_lbl.grid(row=2, column=0)
		
		self.persistence_var = DoubleVar(value=noise_type.persistence)
		self.persistence_var.trace_add("write", self.trace)
		
		persistence_ent = ttk.Entry(self, textvariable=self.persistence_var)
		persistence_ent.grid(row=2, column=1)
		
		persistence_btn = ttk.Button(self, text="?", command=self.random_persistence)
		persistence_btn.grid(row=2, column=2)
		
		#Lacunarity
		lacunarity_lbl = ttk.Label(self, text="Lacunarity:")
		lacunarity_lbl.grid(row=3, column=0)
		
		self.lacunarity_var = DoubleVar(value=noise_type.lacunarity)
		self.lacunarity_var.trace_add("write", self.trace)
		
		lacunarity_ent = ttk.Entry(self, textvariable=self.lacunarity_var)
		lacunarity_ent.grid(row=3, column=1)
		
		lacunarity_btn = ttk.Button(self, text="?", command=self.random_lacunarity)
		lacunarity_btn.grid(row=3, column=2)
		
		#Falloff Type
		falloff_type_lbl = ttk.Label(self, text="Falloff Type:")
		falloff_type_lbl.grid(row=4, column=0)
		
		self.falloff_type_var = StringVar(value=noise_type.falloff_type)
		self.falloff_type_var.trace_add("write", self.trace)
		
		falloff_type_cbx = ttk.Combobox(self, values=["radial", "edge"], textvariable=self.falloff_type_var)
		falloff_type_cbx.grid(row=4, column=1)
		
		falloff_type_btn = ttk.Button(self, text="?", command=self.random_falloff_type)
		falloff_type_btn.grid(row=4, column=2)
		
		#Falloff
		falloff_lbl = ttk.Label(self, text="Falloff:")
		falloff_lbl.grid(row=5, column=0)
		
		self.falloff_var = DoubleVar(value=noise_type.falloff)
		self.falloff_var.trace_add("write", self.trace)
		
		falloff_ent = ttk.Entry(self, textvariable=self.falloff_var)
		falloff_ent.grid(row=5, column=1)
		
		falloff_btn = ttk.Button(self, text="?", command=self.random_falloff)
		falloff_btn.grid(row=5, column=2)
		
		#Min Color
		min_color_lbl = ttk.Label(self, text="Min Color:")
		min_color_lbl.grid(row=6, column=0)
		
		self.min_color_var = StringVar(value=noise_type.min_color)
		self.min_color_var.trace_add("write", self.trace_colors)
		
		self.min_color_btn = Button(self, text="   ", bg=noise_type.min_color, command=lambda:self.get_color(self.min_color_var))
		self.min_color_btn.grid(row=6, column=1)
		
		self.min_color_btn1 = ttk.Button(self, text="?", command=lambda:self.get_random_color(self.min_color_var))
		self.min_color_btn1.grid(row=6, column=2)
		
		#Max Color
		max_color_lbl = ttk.Label(self, text="Max Color:")
		max_color_lbl.grid(row=7, column=0)
		
		self.max_color_var = StringVar(value=noise_type.max_color)
		self.max_color_var.trace_add("write", self.trace_colors)
		
		self.max_color_btn = Button(self, text="   ", bg=noise_type.max_color, command=lambda:self.get_color(self.max_color_var))
		self.max_color_btn.grid(row=7, column=1)
		
		self.max_color_btn1 = ttk.Button(self, text="?", command=lambda:self.get_random_color(self.max_color_var))
		self.max_color_btn1.grid(row=7, column=2)
		
		#Zoom
		zoom_lbl = ttk.Label(self, text="Zoom:")
		zoom_lbl.grid(row=8, column=0)
		
		self.zoom_var = DoubleVar(value=noise_type.zoom)
		self.zoom_var.trace_add("write", self.trace)
		
		zoom_ent = ttk.Entry(self, textvariable=self.zoom_var)
		zoom_ent.grid(row=8, column=1)
		
		zoom_btn = ttk.Button(self, text="?", command=self.random_zoom)
		zoom_btn.grid(row=8, column=2)
		
		#Redistribution
		redistribution_lbl = ttk.Label(self, text="Redistribution:")
		redistribution_lbl.grid(row=9, column=0)
		
		self.redistribution_var = DoubleVar(value=noise_type.redistribution)
		self.redistribution_var.trace_add("write", self.trace)
		
		redistribution_ent = ttk.Entry(self, textvariable=self.redistribution_var)
		redistribution_ent.grid(row=9, column=1)
		
		redistribution_btn = ttk.Button(self, text="?", command=self.random_redistribution)
		redistribution_btn.grid(row=9, column=2)
		
	def trace(self, *args):
		noise_type = self.noise_type
		
		noise_type.seed = self.seed_var.get()
		
		noise_type.octaves = self.octaves_var.get()
		
		noise_type.persistence = self.persistence_var.get()
		
		noise_type.lacunarity = self.lacunarity_var.get()
		
		noise_type.falloff_type = self.falloff_type_var.get()
		
		try:
			noise_type.falloff = self.falloff_var.get()
			
		except TCLError:
			noise_type.falloff = 0
		
		try:
			noise_type.zoom = self.zoom_var.get()
			
		except TclError:
			noise_type.zoom = 1
			
		try:	
			noise_type.redistribution = self.redistribution_var.get()
			
		except TclError:
			noise_type.redistribution = 1
		
	def random_seed(self):
		noise_type = self.noise_type
		min_seed = noise_type.min_seed
		max_seed = noise_type.max_seed
	
		self.seed_var.set(random.randint(min_seed, max_seed))
		
	def random_octaves(self):	
		noise_type = self.noise_type
		min_octaves = noise_type.min_octaves
		max_octaves = noise_type.max_octaves
		
		self.octaves_var.set(random.randint(min_octaves, max_octaves))
		
	def random_persistence(self):
		noise_type = self.noise_type
		
		min_persistence = noise_type.min_persistence
		max_persistence = noise_type.max_persistence
		
		self.persistence_var.set(round(random.uniform(min_persistence, max_persistence), 2))
		
	def random_lacunarity(self):
		noise_type = self.noise_type
		
		min_lacunarity = noise_type.min_lacunarity
		max_lacunarity = noise_type.max_lacunarity
		
		self.lacunarity_var.set(round(random.uniform(min_lacunarity, max_lacunarity), 2))
		
	def random_falloff_type(self):
		noise_type = self.noise_type
		
		self.falloff_type_var.set(random.choice(["radial", "edge"]))
		
	def random_falloff(self):
		noise_type = self.noise_type
		
		min_falloff = noise_type.min_falloff
		max_falloff = noise_type.max_falloff
		
		self.falloff_var.set(round(random.uniform(min_falloff, max_falloff), 2))
		
	def random_zoom(self):
		noise_type = self.noise_type
		
		min_zoom = noise_type.min_zoom
		max_zoom = noise_type.max_zoom
		
		self.zoom_var.set(round(random.uniform(min_zoom, max_zoom), 2))

	def get_color(self, var):
		new_color = colorchooser.askcolor(var.get())[1]
		
		var.set(new_color)
		
	def get_random_color(self, var):
		new_color = helpf.random_hex_color()
		
		var.set(new_color)

	def trace_colors(self, *args):
		noise_type = self.noise_type
		
		min_color = self.min_color_var.get()
		
		self.min_color_btn.config(bg=min_color)
		
		noise_type.min_color = min_color
		
		max_color = self.max_color_var.get()
		
		self.max_color_btn.config(bg=max_color)
		
		noise_type.max_color = max_color
	
	def random_redistribution(self):
		noise_type = self.noise_type
		
		min_redist = noise_type.min_redistribution
		max_redist = noise_type.max_redistribution
		
		self.redistribution_var.set(round((random.uniform(min_redist, max_redist)), 2))
	
class ScrollableFr(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		
		self.sb = ttk.Scrollbar(self, orient=VERTICAL)
		self.sb.grid(row=0, column=1, sticky="ns")
		
		self.can = Canvas(self, yscrollcommand=self.sb.set)
		self.can.grid(row=0, column=0, sticky="nsew")
		
		self.sb.config(command=self.can.yview)
		
		self.fr1 = ttk.Frame(self.can)
		self.fr1.bind("<Configure>", lambda e: self.can.config(scrollregion=self.can.bbox("all")))
		
		item = self.can.create_window(0, 0, window=self.fr1, anchor=NW)
		self.can.bind("<Configure>", lambda e: self.can.itemconfig(item, width=e.width))
		self.can.config(yscrollcommand = self.sb.set)
		
		self.fr1.grid_anchor("n")