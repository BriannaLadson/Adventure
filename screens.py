from tkinter import *
from tkinter import ttk
import os
from terraforge import TerraForge
import threading
import random

import helpfunctions as helpf
import dataparsing
import entities
import commands
import worldgeneration as worldgen

#Screens
class Screen(ttk.Frame):
	def __init__(self, root):
		super().__init__(root)
		
		self.root = root
		
	def display(self):
		self.pack(fill=BOTH, expand=1)
		
	def hide(self):
		self.pack_forget()
		
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
		exit_btn.pack(side=LEFT)
		
class WorldGenerationScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.game = game = root.game
		
		#Title
		title_lbl = ttk.Label(self, text="World Generation", anchor="center")
		title_lbl.pack(fill=X)
		
		#Middle
		middle_fr = ttk.Frame(self)
		middle_fr.pack(fill=BOTH, expand=1)
		
		#Middle - Settings
		settings_fr = ttk.Frame(middle_fr)
		settings_fr.pack(side=LEFT, fill=Y)
		
		self.notebook = WorldSettingsNotebook(settings_fr, game)
		self.notebook.pack(fill=BOTH, expand=1)
		
		#Map
		self.map_can = Canvas(middle_fr, bg="white")
		self.map_can.pack(fill=BOTH, expand=1)
		
		self.generate_btn = ttk.Button(settings_fr, text="Generate", command=self.start_generate)
		self.generate_btn.pack(fill=X)
		
		#Continue
		self.continue_btn = ttk.Button(self, text="Continue", state="disabled", command=self.continue_)
		self.continue_btn.pack(fill=X)
		
	def start_generate(self):
		self.generate_btn.config(state="disabled")
		
		threading.Thread(target=self.generate).start()
		
	def generate(self):
		root = self.root
		game = self.game
		
		#Popup
		popup = GeneratePopup(root, "Generating World...")
		popup.center()
		
		self.map_can.update_idletasks()
		width = self.map_can.winfo_width()
		height = self.map_can.winfo_height()
		
		#Overworld Generator
		self.generator = TerraForge(
			noise_types=game.noise_types,
			biomes=game.biomes,
			map_size=game.world_size,
			image_size=(width, height),
			num_islands=game.num_islands,
			island_spread=game.island_spread,
			min_island_spacing=game.min_island_spacing,
		)
		
		self.generator.generate(output_dir=game.save_path)
		
		game.overworld_generator = self.generator
		
		game.location_map = [
			[None for _ in range(game.world_size)]
			for _ in range(game.world_size)
		]
		
		worldgen.generate_world(game)

		self.map_can.delete("all")
		
		map_img_path = f"{game.save_path}/biome_map.png"

		self.map_img = PhotoImage(file=map_img_path)
		
		self.map_can.create_image(0, 0, anchor="nw", image=self.map_img)

		self.generate_btn.config(state="normal")
		self.continue_btn.config(state="normal")

		popup.destroy()

	def continue_(self):
		root = self.root
		game = self.game
		
		self.generator.wraparound = True
		game.overworld_generator = self.generator
		
		root.character_creation_screen = CharacterCreationScreen(root)
		root.character_creation_screen.display()
		
		self.destroy()
		
class CharacterCreationScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.game = root.game
		
		#Title
		title_lbl = ttk.Label(self, text="Character Creation", anchor="center")
		title_lbl.pack(fill=X)
		
		self.continue_btn = ttk.Button(self, text="Continue", command=self.continue_)
		self.continue_btn.pack(fill=X)
		
	def continue_(self):
		root = self.root
		game = self.game
		
		player = game.player = entities.Player()
		
		game.random_region_placement(player)
		
		helpf.save_data(game.save_path, "game", game)
		
		root.play_screen = PlayScreen(root)
		root.play_screen.display()
		
		self.destroy()
		
class PlayScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		if hasattr(root, "game"):
			game = self.game = root.game
			
		else:
			game = self.game = helpf.get_data(root.save_path, "game")
		
		
		player = self.player = game.player
		
		self.update_tile_map = False
		
		#Info Frame
		info_fr = ttk.Frame(self)
		info_fr.pack(fill=X)
		
		#Info Frame - Location
		location_fr = ttk.Frame(info_fr)
		location_fr.pack(side=LEFT, fill=X, expand=1)
		
		self.location_var = StringVar(value=f"Location: {game.get_location(player)}")
		
		location_lbl = ttk.Label(location_fr, textvariable=self.location_var, anchor="center")
		location_lbl.pack()
		
		#Map
		self.tile_map = TileMap(self, game, game.overworld_generator)
		self.tile_map.pack(fill=BOTH, expand=1)
		
		#Bindings
		root.bind("<+>", self.tile_map.zoom_in)
		root.bind("<minus>", self.tile_map.zoom_out)
		
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
		game = self.game
		player = self.player
		
		self.location_var.set(f"Location: {game.get_location(player)}")
		
		if self.update_tile_map:
			generator = None
			map_type = None
			
			if player.lx is None:
				generator = game.overworld_generator
				map_type = "overworld"
				
			else:
				location = game.location_map[player.gy][player.gx]
				
				seed = player.gy * game.world_size + player.gx + 1
				
				if isinstance(location, entities.Settlement):
					generator = entities.TownMapGenerator(
						location,
						seed,
						game.local_map_size,
					)
					
				else:
					biome_id = game.overworld_generator.get_biome(player.gx, player.gy)["id"]
				
					biome = game.biome_objs[biome_id]
				
					generator = entities.LocalMapGenerator(biome, seed, game.local_map_size)
				
					map_type = "local"
				
			
			game.local_generator = generator
			
			if map_type == "local":
				player.lx, player.ly = generator.get_nearest_walkable(player.lx, player.ly)
			
			self.tile_map.tiles = []
			self.tile_map.generator = generator
			self.tile_map.map_type = map_type
			self.tile_map.update_map()
			
			self.update_tile_map = False

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
			
			root.start_screen.hide()
			
			root.game = game = entities.Game(root.save_path)
			
			dataparsing.load_data(game)
			
			root.world_generation_screen = WorldGenerationScreen(root)
			root.world_generation_screen.display()
			
		else:
			popup = OverwriteSavePopup(root)
			popup.center()
			
		self.destroy()
		
class GeneratePopup(Popup):
	def __init__(self, root, txt):
		super().__init__(root)
		
		ttk.Label(self, text=txt).pack()
		
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
			
			root.start_screen.hide()
			
			root.game = game = entities.Game(root.save_path)
			
			dataparsing.load_data(game)
			
			root.world_generation_screen = WorldGenerationScreen(root)
			root.world_generation_screen.display()
			
		self.destroy()
		
#Widgets
class WorldSettingsNotebook(ttk.Notebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.overworld_tab = OverworldTab(self, game)
		self.add(self.overworld_tab, text="Overworld")
		
		self.region_tab = RegionTab(self, game)
		self.add(self.region_tab, text="Local")
		
class Tab(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		
class OverworldTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.notebook = OverworldNotebook(self, game)
		self.notebook.pack(fill=BOTH, expand=1)
		
class OverworldNotebook(ttk.Notebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.general_tab = OverworldGeneralTab(self, game)
		self.add(self.general_tab, text="General")
		
		self.init_noise_type_tabs()
		
	def init_noise_type_tabs(self):
		game = self.game
		
		for key in game.noise_types:
			tab = NoiseTypeTab(self, game, key)
			
			setattr(self, f"{key}_tab", tab)
			
			self.add(tab, text = key.capitalize())
		
class OverworldGeneralTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		#Map Size
		map_size_fr = ttk.Frame(self)
		map_size_fr.pack()
		
		map_size_lbl = ttk.Label(map_size_fr, text="Map Size:")
		map_size_lbl.pack(side=LEFT)
		
		self.map_size_var = IntVar(value=game.world_size)
		self.map_size_var.trace_add("write", self.trace)
		
		map_size_ent = ttk.Entry(map_size_fr, textvariable=self.map_size_var)
		map_size_ent.pack(side=LEFT)
		
		#Number of Islands
		island_num_fr = ttk.Frame(self)
		island_num_fr.pack()
		
		island_num_lbl = ttk.Label(island_num_fr, text="Number of Islands")
		island_num_lbl.pack(side=LEFT)
		
		self.island_num_var = IntVar(value=1)
		self.island_num_var.trace_add("write", self.trace)
		
		island_num_ent = ttk.Entry(island_num_fr, textvariable=self.island_num_var)
		island_num_ent.pack(side=LEFT)
		
		#Island Spread
		island_spread_fr = ttk.Frame(self)
		island_spread_fr.pack()
		
		island_spread_lbl = ttk.Label(island_spread_fr, text="Island Spread:")
		island_spread_lbl.pack(side=LEFT)
		
		self.island_spread_var = DoubleVar(value=0.3)
		self.island_spread_var.trace_add("write", self.trace)
		
		island_spread_ent = ttk.Entry(island_spread_fr, textvariable=self.island_spread_var)
		island_spread_ent.pack(side=LEFT)
		
	def trace(self, *args):
		game = self.game
		
		#Map Size
		try:
			map_size = self.map_size_var.get()
			
			if not isinstance(map_size, int) or map_size <= 0:
				raise TclError
				
		except TclError:
			self.map_size_var.set(300)
			
		game.world_size = self.map_size_var.get()
		
		#Island Num
		try:
			island_num = self.island_num_var.get()
			
			if not isinstance(island_num, int) or island_num < 0:
				raise TclError
		
		except TclError:
			self.island_num_var.set(1)
			
		game.num_islands = self.island_num_var.get()
		
		#Island Spread
		try:
			island_spread = self.island_spread_var.get()
			
			if not isinstance(island_spread, float) or island_spread < 0:
				raise TclError
		
		except TclError:
			self.island_spread_var.set(0.3)
			
		game.island_spread = self.island_spread_var.get()
		
class RegionTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.notebook = RegionNotebook(self, game)
		self.notebook.pack(fill=BOTH, expand=1)

class RegionNotebook(ttk.Notebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		#Map Size
		map_size_fr = ttk.Frame(self)
		map_size_fr.pack()
		
		map_size_lbl = ttk.Label(map_size_fr, text="Map Size:")
		map_size_lbl.pack(side=LEFT)
		
		self.map_size_var = IntVar(value=game.local_map_size)
		self.map_size_var.trace_add("write", self.trace)
		
		map_size_ent = ttk.Entry(map_size_fr, textvariable=self.map_size_var)
		map_size_ent.pack(side=LEFT)
		
	def trace(self, *args):
		game = self.game
		
		#Map Size
		try:
			map_size = self.map_size_var.get()
			
			if not isinstance(map_size, int) or map_size <= 0:
				raise TclError
		
		except:
			self.map_size_var.set(100)
			
		game.local_map_size = self.map_size_var.get()
		
class NoiseTypeTab(Tab):
	def __init__(self, parent, game, noise_type_key):
		super().__init__(parent)
		
		self.game = game
		
		self.noise_type_key = noise_type_key
		
		self.noise_type = noise_type = game.noise_types[noise_type_key]
		
		#Seed
		seed_fr = ttk.Frame(self)
		seed_fr.pack()
		
		seed_lbl = ttk.Label(seed_fr, text="Seed:")
		seed_lbl.pack(side=LEFT)
		
		self.seed_var = IntVar(value=noise_type["seed"])
		self.seed_var.trace_add("write", self.trace)
		
		seed_ent = ttk.Entry(seed_fr, textvariable=self.seed_var)
		seed_ent.pack(side=LEFT)
		
		seed_btn = ttk.Button(seed_fr, text="?", command=lambda:self.seed_var.set(random.randint(0, 65535)))
		seed_btn.pack(side=LEFT)
		
		#Octaves
		octaves_fr = ttk.Frame(self)
		octaves_fr.pack()
		
		octaves_lbl = ttk.Label(octaves_fr, text="Octaves:")
		octaves_lbl.pack(side=LEFT)
		
		self.octaves_var = IntVar(value=noise_type["octaves"])
		self.octaves_var.trace_add("write", self.trace)
		
		octaves_ent = ttk.Entry(octaves_fr, textvariable=self.octaves_var)
		octaves_ent.pack(side=LEFT)
		
		octaves_btn = ttk.Button(octaves_fr, text="?", command=lambda:self.octaves_var.set(random.randint(1, 10)))
		octaves_btn.pack(side=LEFT)
		
		#Persistence
		persistence_fr = ttk.Frame(self)
		persistence_fr.pack()
		
		persistence_lbl = ttk.Label(persistence_fr, text="Persistence:")
		persistence_lbl.pack(side=LEFT)
		
		self.persistence_var = DoubleVar(value=noise_type["persistence"])
		self.persistence_var.trace_add("write", self.trace)
		
		persistence_ent = ttk.Entry(persistence_fr, textvariable=self.persistence_var)
		persistence_ent.pack(side=LEFT)
		
		persistence_btn = ttk.Button(persistence_fr, text="?", command=lambda:self.persistence_var.set(round(random.uniform(0.01, 1.0), 2)))
		persistence_btn.pack(side=LEFT)
		
		#Lacunarity
		lacunarity_fr = ttk.Frame(self)
		lacunarity_fr.pack()
		
		lacunarity_lbl = ttk.Label(lacunarity_fr, text="Lacunarity:")
		lacunarity_lbl.pack(side=LEFT)
		
		self.lacunarity_var = DoubleVar(value=noise_type["lacunarity"])
		self.lacunarity_var.trace_add("write", self.trace)
		
		lacunarity_ent = ttk.Entry(lacunarity_fr, textvariable=self.lacunarity_var)
		lacunarity_ent.pack(side=LEFT)
		
		lacunarity_btn = ttk.Button(lacunarity_fr, text="?", command=lambda: self.lacunarity_var.set(round(random.uniform(0, 2), 2)))
		lacunarity_btn.pack(side=LEFT)
		
		#Falloff Type
		falloff_fr = ttk.Frame(self)
		falloff_fr.pack()
		
		falloff_lbl = ttk.Label(falloff_fr, text="Falloff Type:")
		falloff_lbl.pack(side=LEFT)
		
		self.falloff_type_var = StringVar(value=noise_type["falloff"]["type"])
		self.falloff_type_var.trace_add("write", self.trace)
		
		falloff_type_cbx = ttk.Combobox(falloff_fr, values=["radial", "edge"], textvariable=self.falloff_type_var)
		falloff_type_cbx.pack(side=LEFT)
		
		#Falloff
		falloff_fr1 = ttk.Frame(self)
		falloff_fr1.pack()
		
		falloff_lbl1 = ttk.Label(falloff_fr1, text="Falloff Strength:")
		falloff_lbl1.pack(side=LEFT)
		
		self.falloff_var = DoubleVar(value=noise_type["falloff"]["strength"])
		self.falloff_var.trace_add("write", self.trace)
		
		falloff_ent1 = ttk.Entry(falloff_fr1, textvariable=self.falloff_var)
		falloff_ent1.pack(side=LEFT)
		
		falloff_btn = ttk.Button(falloff_fr1, text="?", command=lambda:self.falloff_var.set(round(random.uniform(0, 1), 2)))
		falloff_btn.pack(side=LEFT)
		
		#Zoom
		zoom_fr = ttk.Frame(self)
		zoom_fr.pack()
		
		zoom_lbl = ttk.Label(zoom_fr, text="Zoom:")
		zoom_lbl.pack(side=LEFT)
		
		self.zoom_var = DoubleVar(value=noise_type["zoom"])
		self.zoom_var.trace_add("write", self.trace)
		
		zoom_ent = ttk.Entry(zoom_fr, textvariable=self.zoom_var)
		zoom_ent.pack(side=LEFT)
		
		zoom_btn = ttk.Button(zoom_fr, text="?", command=lambda:self.zoom_var.set(round(random.uniform(0.01, 2), 2)))
		zoom_btn.pack(side=LEFT)
		
		#Redistribution
		redistribution_fr = ttk.Frame(self)
		redistribution_fr.pack()
		
		redistribution_lbl = ttk.Label(redistribution_fr, text="Redistribution:")
		redistribution_lbl.pack(side=LEFT)
		
		self.redistribution_var = DoubleVar(value=noise_type["redistribution"])
		self.redistribution_var.trace_add("write", self.trace)
		
		redistribution_ent = ttk.Entry(redistribution_fr, textvariable=self.redistribution_var)
		redistribution_ent.pack(side=LEFT)
		
		redistribution_btn = ttk.Button(redistribution_fr, text="?", command=lambda:self.redistribution_var.set(round(random.uniform(0.01, 2), 2)))
		redistribution_btn.pack(side=LEFT)
		
	def trace(self, *args):
		game = self.game
		noise_type = self.noise_type
		noise_type_key = self.noise_type_key
		
		#Seed
		seed = self.seed_var.get()
		max = 65535
		
		try:
			if not isinstance(seed, int) or seed <= 0 or seed > max:
				raise TclError
			
		except:
			self.seed_var.set(0)
			
		noise_type["seed"] = self.seed_var.get()
		
		#Octaves
		octaves = self.octaves_var.get()
		
		try:
			if not isinstance(octaves, int) or octaves <= 0:
				raise TclError
		
		except TclError:
			self.octaves_var.set(10)
			
		noise_type["octaves"] = self.octaves_var.get()
		
		
		
		#Persistence
		persistence = self.persistence_var.get()
		
		try:
			if not isinstance(persistence, float) or persistence <= 0:
				raise TclError
		
		except TclError:
			self.persistence_var.set(0.5)
			
		noise_type["persistence"] = self.persistence_var.get()
			
		#Lacunarity
		lacunarity = self.lacunarity_var.get()
		
		try:
			if not isinstance(lacunarity, float) or lacunarity <= 0:
				raise TclError
		
		except TclError:
			self.lacunarity_var.set(2.0)
			
		noise_type["lacunarity"] = self.lacunarity_var.get()
			
		#Falloff Type
		noise_type["falloff"]["type"] = self.falloff_type_var.get()
		
		#Falloff
		falloff_strength = self.falloff_var.get()
		
		try:
			if not isinstance(falloff_strength, float) or falloff_strength < 0 or falloff_strength > 1:
				raise TclError
		
		except TclError:
			self.falloff_var.set(0.5)
			
		noise_type["falloff"]["strength"] = self.falloff_var.get()
		
		#Zoom
		zoom = self.zoom_var.get()
		
		try:
			if not isinstance(zoom, float) or zoom <= 0:
				raise TclError
		
		except TclError:
			self.zoom_var.set(1.0)
			
		noise_type["zoom"] = self.zoom_var.get()
		
		#Redistribution
		redistribution = self.redistribution_var.get()
		
		try:
			if not isinstance(redistribution, float) or redistribution <= 0:
				raise TclError
		
		except:
			self.redistribution_var.set(1.0)
			
		noise_type["redistribution"] = self.redistribution_var.get()
			
		game.noise_types[noise_type_key] = noise_type
		
class TileMap(Canvas):
	def __init__(self, parent, game, generator, map_type="overworld"):
		super().__init__(parent, highlightbackground="black", highlightthickness=2)
		
		self.game = game
		self.generator = generator
		self.map_type = map_type
		self.player = player = game.player
		
		self.min_tiles = 11
		self.max_tiles = 51
		
		self.map_size = 11
		
		self.tiles = []
		
		self.bind("<Configure>", self.update_map)
		
	def zoom_in(self, event=None):
		self.map_size -= 2
		
		if self.map_size < self.min_tiles:
			self.map_size = self.min_tiles
			
		self.tiles = []
		
		self.update_map()
		
	def zoom_out(self, event=None):
		self.map_size += 2
		
		if self.map_size > self.max_tiles:
			self.map_size = self.max_tiles
			
		self.tiles = []
		
		self.update_map()
		
	def update_map(self, event=None):
		self.update_idletasks()
		
		self.draw_tiles()
		
		self.draw_buildings()
		
		self.draw_locations()
		
		self.draw_player()
		
	def draw_tiles(self):
		canvas_width = self.winfo_width()
		canvas_height = self.winfo_height()
		
		tile_width = canvas_width / self.map_size
		tile_height = canvas_height / self.map_size
		
		if not self.tiles:
			self.delete("tile")
			
			outline_width = getattr(self.generator, "tile_outline_width", 2)
			outline_color = getattr(self.generator, "tile_outline_color", "black")
			
			for sy in range(self.map_size):
				row = []
				
				for sx in range(self.map_size):
					tx = sx * tile_width
					ty = sy * tile_height
					
					rect = self.create_rectangle(
						tx, ty,
						tx + tile_width, ty + tile_height,
						tags="tile",
						width=outline_width,
						outline=outline_color,
					)
					
					row.append(rect)
					
				self.tiles.append(row)
				
		half = self.map_size // 2
		
		player = self.player
		
		px, py = self.get_player_coords()
		
		for sy in range(self.map_size):
			for sx in range(self.map_size):
				wx = px - half + sx
				wy = py - half + sy
				
				if self.generator.wraparound:
					wx %= self.generator.map_size
					wy %= self.generator.map_size
					
					color = self.generator.tile_color(wx, wy)
					
				else:
					
					if 0 <= wx < self.generator.map_size and 0 <= wy < self.generator.map_size:
						color = self.generator.tile_color(wx, wy)
						
					else:
						color = "black"
					
				tx = sx * tile_width
				ty = sy * tile_height
				
				rect = self.tiles[sy][sx]
				
				self.coords(
					rect,
					tx, ty,
					tx + tile_width, ty + tile_height,
				)
				
				self.itemconfigure(rect, fill=color)
		
	def draw_locations(self):
		if hasattr(self, "location_items"):
			for item in self.location_items:
				self.delete(item)

		self.location_items = []

		if self.map_type != "overworld":
			return

		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size

		half = self.map_size // 2
		px, py = self.get_player_coords()

		for screen_y in range(self.map_size):
			for screen_x in range(self.map_size):
				wx = px - half + screen_x
				wy = py - half + screen_y

				if self.generator.wraparound:
					wx %= self.generator.map_size
					wy %= self.generator.map_size
				else:
					if not (0 <= wx < self.generator.map_size and 0 <= wy < self.generator.map_size):
						continue

				location = self.game.location_map[wy][wx]

				if location is None:
					continue

				cx = (screen_x + 0.5) * tile_width
				cy = (screen_y + 0.5) * tile_height

				font_size = int(min(tile_width, tile_height) * 0.5)

				item = self.create_text(
					cx, cy,
					text=location.char,
					fill=location.char_color,
					font=("TkDefaultFont", font_size, "bold")
				)

				self.location_items.append(item)
				self.tag_raise(item)
		
	def draw_player(self):
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		center = self.map_size // 2
		
		cx = (center + 0.5) * tile_width
		cy = (center + 0.5) * tile_height
		
		font_size = int(min(tile_width, tile_height) * 0.5)
		
		if not hasattr(self, "player_item"):
			self.player_item = self.create_text(
				cx, cy,
				text=self.player.char,
				font=("TkDefaultFont", font_size, "bold")
			)
			
		else:
			self.coords(self.player_item, cx, cy)
			self.itemconfig(self.player_item, font=("TkDefaultFont", font_size, "bold"))
			
		self.tag_raise(self.player_item)
		
	def draw_buildings(self):
		if hasattr(self, "building_items"):
			for item in self.building_items:
				self.delete(item)
				
		self.building_items = []
		
		if not isinstance(self.generator, entities.TownMapGenerator):
			return
			
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		half = self.map_size // 2
		px, py = self.get_player_coords()
		
		for building in self.generator.generator.buildings:
			x = building["x"]
			y = building["y"]
			w = building["width"]
			h = building["height"]
			
			screen_x = x - px + half
			screen_y = y - py + half
			
			if screen_x + w < 0 or screen_y + h < 0:
				continue
				
			if screen_x >= self.map_size or screen_y >= self.map_size:
				continue
				
			x0 = screen_x * tile_width
			y0 = screen_y * tile_height
			x1 = (screen_x + w) * tile_width
			y1 = (screen_y + h) * tile_height
			
			item = self.create_rectangle(
				x0, y0,
				x1, y1,
				fill=building["color"],
				outline="black",
				width=2,
			)
			
			self.building_items.append(item)
			
			door_x, door_y = building["door"]
			
			door_screen_x = door_x - px + half
			door_screen_y = door_y - py + half

			if 0 <= door_screen_x < self.map_size and 0 <= door_screen_y < self.map_size:
				dx0 = door_screen_x * tile_width
				dy0 = door_screen_y * tile_height
				
				dx1 = (door_screen_x + 1) * tile_width
				dy1 = (door_screen_y + 1) * tile_height
				
				door_item = self.create_rectangle(
					dx0, dy0,
					dx1, dy1,
					fill="#FFD700",
					outline="black",
					width=1,
				)
				
				self.building_items.append(door_item)
		
	def move_left(self, event=None):
		if self.player_x > 0:
			self.player_x -= 1
			
			self.update_map()
			
	def move_right(self, event=None):
		if self.player_x < self.generator.map_size - 1:
			self.player_x += 1
			
			self.update_map()
			
	def move_up(self, event=None):
		if self.player_y > 0:
			self.player_y -= 1
			
			self.update_map()
			
	def move_down(self, event=None):
		if self.player_y < self.generator.map_size - 1:
			self.player_y += 1
			
			self.update_map()
			
	def get_player_coords(self):
		if self.map_type == "overworld":
			return self.player.gx, self.player.gy
			
		else:
			return self.player.lx, self.player.ly