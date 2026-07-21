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
		
		load_game_btn = ttk.Button(fr, text="Load Game", command=lambda:LoadSavePopup(root))
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
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		scr_fr = self.scrollable_frame.scrolling_frame
		
		#Race
		race_fr = ttk.Frame(scr_fr)
		race_fr.pack(pady=5)
		
		race_lbl = ttk.Label(race_fr, text="Race", anchor="center")
		race_lbl.pack()
		
		self.race_options = {
			race.name: race for race in self.game.race_objs.values()
		}
		
		self.race_var = StringVar(value=list(self.race_options.keys())[0])
		
		race_cbx = ttk.Combobox(race_fr, textvariable=self.race_var, values=list(self.race_options.keys()), state="readonly")
		race_cbx.pack()
		
		#Starting Currency
		start_currency_fr = ttk.Frame(scr_fr)
		start_currency_fr.pack(pady=5)
		
		start_currency_lbl = ttk.Label(start_currency_fr, text="Starting Currency", anchor="center")
		start_currency_lbl.grid(row=0, column=0, columnspan=2, sticky="we")
		
		self.currency_options = {
			currency.name: currency for currency in self.game.coin_objs.values()
		}
		
		self.currency_var = StringVar(value=list(self.currency_options.keys())[0])
		
		currency_cbx = ttk.Combobox(start_currency_fr, textvariable=self.currency_var, values=list(self.currency_options.keys()), state="readonly")
		currency_cbx.grid(row=1, column=0, padx=5)
		
		self.currency_quantity_var = StringVar(value=100)
		
		currency_quantity_ent = ttk.Entry(start_currency_fr, textvariable=self.currency_quantity_var)
		currency_quantity_ent.grid(row=1, column=1)
		
		#Starting Location
		start_loc_fr = ttk.Frame(scr_fr)
		start_loc_fr.pack(pady=5)
		
		start_loc_lbl = ttk.Label(start_loc_fr, text="Starting Location", anchor="center")
		start_loc_lbl.pack()
		
		self.start_loc_var = StringVar(value="Random")
		self.start_loc_var.trace_add("write", self.trace)
		
		start_loc_cbx = ttk.Combobox(start_loc_fr, textvariable=self.start_loc_var, values=["Random", "Random Settlement"], state="readonly")
		start_loc_cbx.pack()
		
		self.continue_btn = ttk.Button(self, text="Continue", command=self.continue_, state=DISABLED)
		self.continue_btn.pack(fill=X)
		
		self.trace()
		
	def trace(self, *args):
		state=NORMAL
		
		try:
			value = int(self.currency_quantity_var.get())
			
			if value < 0:
				raise ValueError
		
		except ValueError:
			state=DISABLED
		
		self.continue_btn.config(state=state)
		
	def continue_(self):
		root = self.root
		game = self.game
		
		race_name = self.race_var.get()
		race = self.race_options[race_name]
		
		player = game.player = entities.Player(race)
		
		#Currency
		currency_name = self.currency_var.get()
		currency = self.currency_options[currency_name]
		
		currency_quantity = int(self.currency_quantity_var.get())
		
		player.wallet.add_coins(currency.id, currency_quantity)
		
		#Initial Placement
		if self.start_loc_var.get() == "Random":
			game.random_region_placement(player)
			
		else:
			game.random_settlement_placement(player)
			
		game.discover_nearby_locations(player)
		
		game.entities.append(player)
		
		helpf.save_data(game.save_path, "game", game)
		
		root.play_screen = PlayScreen(root)
		root.play_screen.display()
		
		self.destroy()
		
class PlayScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.can_process_input = True
		
		if hasattr(root, "game"):
			game = self.game = root.game
			
		else:
			game = self.game = helpf.get_data(root.save_path, "game")
			
		self.calendar = calendar = game.calendar
		
		player = self.player = game.player
		
		self.update_tile_map = False
		
		self.building_popup_types = {
			"trade": TradePopup,
		}
		
		#Info Frame
		info_fr = ttk.Frame(self)
		info_fr.pack(fill=X)
		
		#Info Frame - Time & Date
		calendar_fr = ttk.Frame(info_fr)
		calendar_fr.pack(fill=X, expand=1)
		
		self.time_var = StringVar(value=f"Time: {calendar.time_string()}")
		
		time_lbl = ttk.Label(calendar_fr, textvariable=self.time_var, anchor="center")
		time_lbl.pack()
		
		self.date_var = StringVar(value=f"Date: {calendar.date_string()}")
		
		date_lbl = ttk.Label(calendar_fr, textvariable=self.date_var, anchor="center")
		date_lbl.pack()
		
		#Info Frame - Location
		location_fr = ttk.Frame(info_fr)
		location_fr.pack(fill=X, expand=1)
		
		self.location_var = StringVar(value=f"Location: {game.get_location(player)}")
		
		location_lbl = ttk.Label(location_fr, textvariable=self.location_var, anchor="center")
		location_lbl.pack()
		
		#Map
		generator, map_type = self.get_current_map_data()
		
		self.tile_map = TileMap(self, game, generator, map_type=map_type)
		self.tile_map.pack(fill=BOTH, expand=1)
		
		#Bindings
		root.protocol("WM_DELETE_WINDOW", self.open_menu)
		
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
		
		root.bind("@", lambda e:CharacterSheetPopup(e, root, game))
		
		root.bind("<Escape>", self.open_menu)
		
		root.bind("g", lambda e: commands.process_cmd(e, self, "pickup_item"))
		
	def update_screen(self):
		game = self.game
		player = self.player
		
		self.update_calendar()
		
		self.location_var.set(f"Location: {game.get_location(player)}")
		
		if not self.update_tile_map:
			return
			
		generator, map_type = self.get_current_map_data()
		
		if map_type == "local":
			player.lx, player.ly = generator.get_nearest_walkable(
				player.lx, player.ly,
			)
			
		self.tile_map.tiles = []
		self.tile_map.generator = generator
		self.tile_map.map_type = map_type
		self.tile_map.update_map()
		
		self.update_tile_map = False
			
	def update_calendar(self):
		calendar = self.calendar
		
		self.time_var.set(f"Time: {calendar.time_string()}")
		
		self.date_var.set(f"Date: {calendar.date_string()}")
		
	def discover_locations(self):
		game = self.game
		player = self.player
		
		if player.lx is not None:
			return []
			
		return game.discover_nearby_locations(player)
		
	def handle_discovered_locations(self, locations):
		if not locations:
			return
			
		self.can_process_input = False
		
		txt = "\n".join(f"You discovered {location.name}!" for location in locations)
		
		popup = SimplePopup(self.root, txt)
			
		popup.center()
		
	def handle_player_death(self):
		self.can_process_input = False
		
		popup = DeathPopup(self.root)
		popup.center()
		
	def check_building_interaction(self):
		game = self.game
		player = self.player
		
		if player.lx is None:
			return
			
		if not isinstance(game.local_generator, entities.TownMapGenerator):
			return
			
		building = game.local_generator.get_building_by_door(player.lx, player.ly)
		
		if building is None:
			return
			
		return building
		
	def handle_building_interaction(self, building):
		popup_type = getattr(building.building_type, "popup_type", None)
		popup_cls = self.building_popup_types.get(popup_type)
		
		if popup_cls is None:
			return
			
		popup = popup_cls(self.root, building)
		popup.center()
		
	def handle_low_needs(self, low_needs):
		self.can_process_input = False
		
		txt = "\n".join(
			f"Your {need_id} is getting low." for need_id in low_needs
		)
		
		popup = SimplePopup(self.root, txt)
		popup.center()

	def open_menu(self, event=None):
		if not self.can_process_input:
			return
			
		self.can_process_input = False
		
		popup = MenuPopup(self.root)
		popup.center()
		
	def get_current_map_data(self):
		game = self.game
		player = self.player
		
		if player.lx is None:
			return game.overworld_generator, "overworld"
			
		location = game.location_map[player.gy][player.gx]
		seed = player.gy * game.world_size + player.gx + 1
		
		if isinstance(location, entities.Settlement):
			generator = entities.TownMapGenerator(
				game,
				location,
				seed,
				game.local_map_size,
			)
			
		else:
			biome_id = game.overworld_generator.get_biome(player.gx, player.gy)["id"]
			biome = game.biome_objs[biome_id]
			generator = entities.LocalMapGenerator(biome, seed, game.local_map_size)
			
		game.local_generator = generator
		
		return generator, "local"
		
	def pickup_item(self, first_inventory, second_inventory, first_inv_text, second_inv_text):
		root = self.root
		game = self.game
		player = self.player
		
		popup = InventoryTransferPopup(root, game, first_inventory, second_inventory, first_inv_text, second_inv_text)
		popup.center()

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
			game.init_economy()
			
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
			game.init_economy()
			
			root.world_generation_screen = WorldGenerationScreen(root)
			root.world_generation_screen.display()
			
		self.destroy()
	
class SimplePopup(Popup):
	def __init__(self, root, txt):
		super().__init__(root)
		
		self.play_screen = None
		
		if hasattr(root, "play_screen"):
			self.play_screen = root.play_screen
		
		ttk.Label(self, text=txt).pack()
		
		ttk.Button(self, text="OK", command=self.close).pack()
		
		self.center()
		
	def close(self):
		if not self.play_screen == None:
			self.play_screen.can_process_input = True
			
		self.destroy()
		
class TradePopup(Popup):
	def __init__(self, root, building):
		super().__init__(root)
		
		self.play_screen = play_screen = None
		
		if hasattr(root, "play_screen"):
			self.play_screen = play_screen = root.play_screen
			
		self.game = game = self.play_screen.game
		self.player = player = game.player
			
		self.building = building
		
		self.settlement = settlement = building.settlement
		
		sub_economy = settlement.sub_economy
		
		self.currency_type = currency_type = settlement.currency
		self.currency_name = currency_name = game.coin_objs[currency_type].name
		self.settlement_currency_quantity = settlement_currency_quantity = settlement.wallet.get_quantity(currency_type)
		
		self.settlement_currency_var = StringVar(value=f"{building.get_name()} ({currency_name}: {settlement_currency_quantity})")	
		ttk.Label(self, textvariable=self.settlement_currency_var, anchor="center").pack(fill=X)
		
		self.player_currency_quantity = player_currency_quantity = player.wallet.get_quantity(currency_type)
		
		self.player_currency_var = StringVar(value=f"You ({currency_name}: {player_currency_quantity})")
		ttk.Label(self, textvariable=self.player_currency_var, anchor="center").pack(fill=X)
		
		self.trade_nb = TradeNotebook(self, root, building)
		self.trade_nb.pack(fill=BOTH, expand=1)
		
		ttk.Button(self, text="OK", command=self.close).pack(fill=X)
		
	def close(self):
		if self.play_screen is not None:
			self.play_screen.can_process_input = True
			
		self.destroy()
		
	def update_popup(self):
		settlement = self.settlement
		player = self.player
		currency_type = self.currency_type
		currency_name = self.currency_name
		
		self.settlement_currency_quantity = settlement_currency_quantity = settlement.wallet.get_quantity(currency_type)
		self.player_currency_quantity = player_currency_quantity = player.wallet.get_quantity(currency_type)
		
		self.settlement_currency_var.set(f"{self.building.get_name()} ({currency_name}: {settlement_currency_quantity})")
		self.player_currency_var.set(f"You ({currency_name}: {player_currency_quantity})")
		
class CharacterSheetPopup(Popup):
	def __init__(self, event, root, game):
		super().__init__(root)
		
		self.game = game
		self.player = player = game.player
		
		ttk.Label(self, text="Character Sheet", anchor="center").pack(fill=X)
		
		self.character_sheet_nb = CharacterSheetNotebook(self, game)
		self.character_sheet_nb.pack(fill=BOTH, expand=1)
		
		ttk.Button(self, text="Close", command=self.destroy).pack(fill=X)
		
		self.center()
		
class ItemPopup(Popup):
	def __init__(self, root, game, item_id, quantity=1, parent_tab=None):
		super().__init__(root)
		
		self.parent_tab = parent_tab
		
		self.game = game
		self.item_id = item_id
		self.quantity = quantity
		self.item = item = game.item_type_objs[item_id]
		
		ttk.Label(self, text=self.item.name, anchor="center").pack(fill=X)
		
		ttk.Label(self, text=f"Quantity: {quantity}", anchor="center").pack(fill=X)
		
		value = getattr(self.item, "value", getattr(self.item, "base_value", 0))
		ttk.Label(self, text=f"Base Value: {value}", anchor="center").pack(fill=X)
		
		ttk.Label(self, text=item.description, wraplength=300, justify="center").pack(fill=BOTH, expand=1)
		
		# Needs
		need_values = getattr(item, "need_values", {})
		
		if need_values:
			for need_id, amount in need_values.items():
				ttk.Label(
					self,
					text=f"{need_id.capitalize()}: +{amount}",
					anchor="center"
				).pack(fill=X)
			
		self.action_funcs = {
			"consume": self.consume_item,
			"drop": self.drop_item,
		}
		
		actions = getattr(item, "actions", [])
		
		if actions:
			self.scrollable_frame = ScrollableFrame(self)
			self.scrollable_frame.pack(fill=BOTH, expand=1)
			
			self.populate_actions(actions)
		
		ttk.Button(self, text="Close", command=self.destroy).pack(fill=X)
		
		self.center()
		
	def populate_actions(self, actions):
		scr_fr = self.scrollable_frame.scrolling_frame
		
		for action in actions:
			func = self.action_funcs.get(action)
			
			if func is None:
				continue
				
			btn = ttk.Button(
				scr_fr,
				text=action.capitalize(),
				command=func,
			)
			btn.pack(fill=X)
			
	def consume_item(self):
		player = self.game.player
		
		if player.consume_item(self.item_id, self.game):
			sheet = self.parent_tab.winfo_toplevel()
			nb = sheet.character_sheet_nb
			
			inventory_notebook = nb.tabs["Inventory"]
			inventory_notebook.tabs["Items"].populate()
			
			nb.tabs["Health"].tabs["Needs"].populate()
			
			self.destroy()
			
	def drop_item(self):
		player = self.game.player
		
		if player.lx == None or player.ly == None or player.lz == None:
			return
			
		if player.drop_item(self.item_id, self.game):
			sheet = self.parent_tab.winfo_toplevel()
			nb = sheet.character_sheet_nb
			
			inventory_notebook = nb.tabs["Inventory"]
			inventory_notebook.tabs["Items"].populate()
			
			self.destroy()
			
class DeathPopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		self.game = game = root.game
		self.player = player = game.player
		
		reason = player.get_death_reason()
		
		ttk.Label(self, text="You died.", anchor="center").pack(fill=X)
		
		if reason is not None:
			ttk.Label(
				self,
				text=f"Cause of Death: {reason.capitalize()}",
				anchor="center"
			).pack(fill=X)
		
		self.continue_btn = ttk.Button(self, text="Continue", command=self.continue_)
		self.continue_btn.pack(fill=X)
		
	def continue_(self):
		root = self.root
		game = root.game
		player = game.player
		
		if player in game.entities:
			game.entities.remove(player)
			
		if hasattr(root, "play_screen"):
			root.play_screen.destroy()
		
		root.character_creation_screen = CharacterCreationScreen(root)
		root.character_creation_screen.display()
		
		self.destroy()
		
class MenuPopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		ttk.Label(self, text="Menu", anchor="center").pack(fill=X)
		
		exit_btn = ttk.Button(self, text="Save & Exit", command=self.save_and_exit)
		exit_btn.pack(fill=X)
		
		close_btn = ttk.Button(self, text="Close", command=self.close)
		close_btn.pack(fill=X)
		
		self.center()
		
	def close(self):
		root = self.root
		
		root.play_screen.can_process_input = True
		
		self.destroy()
		
	def save_and_exit(self):
		root = self.root
		game = root.game
		
		helpf.save_data(game.save_path, "game", game)
		
		root.protocol("WM_DELETE_WINDOW", root.destroy)
		
		root.start_screen = StartScreen(root)
		root.start_screen.display()
		
		root.play_screen.destroy()
		
		self.destroy()
		
class LoadSavePopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		self.selected_save = None
		
		ttk.Label(self, text="Load Save", anchor="center").pack(fill=X)
		
		self.save_scr_lbx = ScrollableListbox(self)
		self.save_scr_lbx.pack(fill=BOTH, expand=1)
		
		self.populate()
		
		btn_fr = ttk.Frame(self)
		btn_fr.pack(fill=X)
		
		load_btn = ttk.Button(btn_fr, text="Load", command=self.load)
		load_btn.pack(side=LEFT, fill=X)
		
		close_btn = ttk.Button(btn_fr, text="Close", command=self.destroy)
		close_btn.pack(side=LEFT, fill=X)
		
		self.center()
		
	def populate(self):
		if not os.path.isdir("saves"):
			return
			
		for save_name in os.listdir("saves"):
			save_path = os.path.join("saves", save_name)
			
			if os.path.isdir(save_path):
				self.save_scr_lbx.insert(END, save_name)
				
	def load(self):
		selected = self.save_scr_lbx.curselection()
		
		if not selected:
			return
			
		save_name = self.save_scr_lbx.get(selected[0])
		
		root = self.root
		
		root.save_path = os.path.join("saves", save_name, "game_data")
		
		root.game = helpf.get_data(root.save_path, "game")
		
		root.start_screen.hide()
		
		root.play_screen = PlayScreen(root)
		root.play_screen.display()
		
		self.destroy()
		
class InventoryTransferPopup(Popup):
	def __init__(self, root, game, first_inventory, second_inventory, first_inv_text="Inventory", second_inv_text="Inventory"):
		super().__init__(root)
		
		self.game = game
		
		self.first_inventory = first_inventory
		self.second_inventory = second_inventory
		
		top_fr = ttk.Frame(self)
		top_fr.pack(fill=BOTH, expand=1)
		
		self.first_inventory_fr = ttk.Frame(top_fr)
		self.first_inventory_fr.pack(side=LEFT, fill=Y)
		
		first_inventory_lbl = ttk.Label(self.first_inventory_fr, text=first_inv_text, anchor="center")
		first_inventory_lbl.pack(fill=X)
		
		self.first_inventory_scr_fr = ScrollableFrame(self.first_inventory_fr)
		self.first_inventory_scr_fr.pack(fill=BOTH, expand=1)
		
		self.first_inventory_btn = ttk.Button(self.first_inventory_fr, text="Transfer All", command=lambda: self.transfer_all(self.first_inventory, self.second_inventory))
		self.first_inventory_btn.pack(fill=X)
		
		self.second_inventory_fr = ttk.Frame(top_fr)
		self.second_inventory_fr.pack(side=LEFT, fill=Y)
		
		second_inventory_lbl = ttk.Label(self.second_inventory_fr, text=second_inv_text, anchor="center")
		second_inventory_lbl.pack(fill=X)
		
		self.second_inventory_scr_fr = ScrollableFrame(self.second_inventory_fr)
		self.second_inventory_scr_fr.pack(fill=BOTH, expand=1)
		
		self.second_inventory_btn = ttk.Button(self.second_inventory_fr, text="Transfer All", command=lambda: self.transfer_all(self.second_inventory, self.first_inventory))
		self.second_inventory_btn.pack(fill=X)

		self.close_btn = ttk.Button(self, text="Close", command=self.close)
		self.close_btn.pack(fill=X)
		
		self.populate()
		
		self.center()
		
	def populate_inventory(self, scroll_frame, source_inventory, target_inventory):
		frame = scroll_frame.scrolling_frame
		
		for widget in frame.winfo_children():
			widget.destroy()
			
		for item_id, quantity in source_inventory.get_items():
			item_frame = ttk.Frame(frame)
			item_frame.pack(fill=X)
			
			item = self.game.item_type_objs[item_id]
			
			ttk.Label(
				item_frame,
				text=f"{item.name} x{quantity}",
				anchor="center"
			).pack(side=LEFT, fill=X, expand=True)
			
			ttk.Button(
				item_frame,
				text="Move",
				command=lambda i=item_id, s=source_inventory, t=target_inventory: self.move_item(s, t, i, 1)
			).pack(side=RIGHT)
			
			ttk.Button(
				item_frame,
				text="Move All",
				command=lambda i=item_id, q=quantity, s=source_inventory, t=target_inventory: self.move_item(s, t, i, q)
			).pack(side=RIGHT)
			
	def move_item(self, source_inventory, target_inventory, item_id, quantity):
		if source_inventory.remove_item(item_id, quantity):
			target_inventory.add_item(item_id, quantity)
			
		self.populate()
		
	def transfer_all(self, source_inventory, target_inventory):
		items = list(source_inventory.get_items())
		
		for item_id, quantity in items:
			source_inventory.remove_item(item_id, quantity)
			target_inventory.add_item(item_id, quantity)
			
		self.populate()
		
	def populate(self):
		self.populate_inventory(self.first_inventory_scr_fr, self.first_inventory, self.second_inventory)
		
		self.populate_inventory(self.second_inventory_scr_fr, self.second_inventory, self.first_inventory)
		
	def close(self):
		self.destroy()

#Widgets
class ScrollableListbox(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.listbox = Listbox(self)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		
		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
		self.scrollbar.pack(side=RIGHT, fill=Y)
		
		self.listbox.configure(yscrollcommand=self.scrollbar.set)
		
	def insert(self, *args):
		return self.listbox.insert(*args)
		
	def curselection(self):
		return self.listbox.curselection()
		
	def get(self, *args):
		return self.listbox.get(*args)
		
	def delete(self, *args):
		return self.listbox.delete(*args)

class WorldSettingsNotebook(ttk.Notebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.overworld_tab = OverworldTab(self, game)
		self.add(self.overworld_tab, text="Overworld")
		
		self.region_tab = RegionTab(self, game)
		self.add(self.region_tab, text="Local")
		
class CustomNotebook(ttk.Notebook):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.tabs = {}
		
	def init_tabs(self):
		for tab_name, tab in self.tabs.items():
			self.add(tab, text=tab_name)
		
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

#Character Sheet		
class CharacterSheetNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Crafting": CraftingTab(self, game),
			"Health": HealthNotebook(self, game),
			"Inventory": InventoryNotebook(self, game),
			"Memory": MemoryNotebook(self, game),
		}
		
		self.init_tabs()
		
class CraftingTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = game.player
		
		self.crafting_professions = {
			profession.name: profession for profession in game.profession_objs.values() if profession.can_craft
		}
		
		self.profession_var = StringVar()
		
		self.crafting_categories_cbx = ttk.Combobox(self, textvariable=self.profession_var, values=list(self.crafting_professions.keys()), state="readonly")
		self.crafting_categories_cbx.pack()
		
		self.crafting_categories_cbx.bind("<<ComboboxSelected>>", self.update_recipes)
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		if self.crafting_professions:
			first_profession = list(self.crafting_professions.keys())[0]
			
			self.profession_var.set(first_profession)
			
			self.update_recipes()
	
	def update_recipes(self, event=None):
		scr_fr = self.scrollable_fr.scrolling_frame
		helpf.destroy_children_widgets(scr_fr)
		
		profession_name = self.profession_var.get()
		profession = self.crafting_professions.get(profession_name)
		
		if profession is None:
			return
			
		for item_id in profession.outputs:
			item = self.game.item_type_objs[item_id]
			
			btn = ttk.Button(
				scr_fr,
				text=item.name,
			)
			btn.pack(fill=X)
	
class HealthNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.tabs = {
			"Needs": NeedsTab(self, game)
		}
		
		self.init_tabs()
		
class NeedsTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = player = game.player
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		scr_fr = self.scrollable_frame.scrolling_frame
		helpf.destroy_children_widgets(scr_fr)
		
		for need_id, value in self.player.needs.items():
			need = self.player.race.needs[need_id]
			max_value = need["max"]
			
			bar = ProgressBar(
				scr_fr, 
				value=value, 
				max_value=max_value, 
				text=f"{need_id.capitalize()}: {value} / {max_value}"
			)
			bar.pack(pady=5)
	
class MemoryNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Locations": LocationsTab(self, game),
		}
		
		self.init_tabs()
		
class LocationsTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = player = game.player
		
		known_location_quantity = game.get_discovered_locations_quantity(player)
		location_quantity = len(game.settlements)
		
		ttk.Label(self, text=f"Discovered Locations: {known_location_quantity} / {location_quantity}", anchor="center").pack(fill=X)
		
		self.sort_var = StringVar(value="Name")
		
		sort_cbx = ttk.Combobox(
			self,
			textvariable=self.sort_var,
			values=["Name", "Distance"],
			state="readonly"
		)
		sort_cbx.pack(fill=X)
		sort_cbx.bind("<<ComboboxSelected>>", lambda e:self.populate())
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		player = self.player
		scr_fr = self.scrollable_fr.scrolling_frame
		
		helpf.destroy_children_widgets(scr_fr)
		
		locations = list(player.memory.known_locations.values())
		
		if self.sort_var.get() == "Name":
			locations.sort(key=lambda location: location.name)
			
		elif self.sort_var.get() == "Distance":
			locations.sort(
				key=lambda location: abs(location.gx - player.gx) + abs(location.gy - player.gy)
			)
			
		for location in locations:
			lbl = ttk.Label(
				scr_fr,
				text=f"{location.name} ({location.gx},{location.gy})"
			)
			lbl.pack(fill=X)
			
class InventoryNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Items": ItemsTab(self, game),
			"Wallet": WalletTab(self, game),
		}
		
		self.init_tabs()
		
class ItemsTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = player = game.player
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		player = self.player
		scr_fr = self.scrollable_fr.scrolling_frame
		
		helpf.destroy_children_widgets(scr_fr)
		
		for item_id, quantity in player.inventory.get_items():
			item = self.game.item_type_objs[item_id]
			
			btn = ttk.Button(
				scr_fr, 
				text=f"{item.name} x{quantity}",
				command=lambda item_id=item_id, quantity=quantity: ItemPopup(
					self.winfo_toplevel(),
					self.game,
					item_id,
					quantity,
					parent_tab=self,
				)
			)
			btn.pack(fill=X)
			
class WalletTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		
		self.game = game
		self.player = player = game.player
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		game = self.game
		player = self.player
		wallet = player.wallet
		scr_fr = self.scrollable_fr.scrolling_frame
		
		helpf.destroy_children_widgets(scr_fr)
		
		for key, val in wallet.coins.items():
			currency_name = game.coin_objs[key].name
			
			lbl = ttk.Label(scr_fr, text=f"{currency_name}: {val}", anchor="center")
			lbl.pack(fill=X)

#Other Widgets		
class ScrollableFrame(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)

		# Create & Display Canvas/Scrollbar
		self.canvas = Canvas(self)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

		self.scrollbar = ttk.Scrollbar(
			self,
			orient="vertical",
			command=self.canvas.yview,
		)
		self.scrollbar.pack(side=RIGHT, fill=Y)

		self.scrolling_frame = ttk.Frame(self.canvas)

		# Connect Canvas and Scrollbar
		self.canvas.configure(
			yscrollcommand=self.scrollbar.set
		)

		# Add Scrolling Frame to Canvas
		self.canvas_window = self.canvas.create_window(
			(0, 0),
			window=self.scrolling_frame,
			anchor="nw",
		)

		self.scrolling_frame.bind(
			"<Configure>",
			self.update_scrollregion,
		)

		self.canvas.bind(
			"<Configure>",
			self.resize_frame,
		)

	def update_scrollregion(self, event=None):
		# Update Scrollregion when Scrolling Frame size changes
		self.canvas.configure(
			scrollregion=self.canvas.bbox("all")
		)

	def resize_frame(self, event=None):
		# Makes Scrolling Frame match Canvas width
		canvas_width = event.width

		self.canvas.itemconfigure(
			self.canvas_window,
			width=canvas_width,
		)
		
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
		
		self.draw_dropped_items()
		
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

				location = self.player.memory.known_locations.get((wx, wy))

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
		
		for building in self.generator.buildings:
			x = building.x
			y = building.y
			w = building.width
			h = building.height
			
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
				fill=building.color,
				outline="black",
				width=2,
			)
			
			self.building_items.append(item)
			
			door_x, door_y = building.door
			
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
				
	def draw_dropped_items(self):
		if hasattr(self, "dropped_items"):
			for item in self.dropped_items:
				self.delete(item)
				
		self.dropped_items = []
		
		if not isinstance(self.generator, entities.TownMapGenerator):
			return
			
		settlement = self.generator.settlement
		
		if not hasattr(settlement, "dropped_items"):
			return
			
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		half = self.map_size // 2
		
		px, py = self.get_player_coords()
		
		for (x, y, z), inventory in settlement.dropped_items.items():
			if not inventory.get_items():
				continue
				
			screen_x = x - px + half
			screen_y = y - py + half
			
			if not (0 <= screen_x < self.map_size and 0 <= screen_y < self.map_size):
				continue
				
			cx = (screen_x + 0.5) * tile_width
			cy = (screen_y + 0.7) * tile_height
			
			item = self.create_text(
				cx,
				cy,
				text="*",
				font=("TkDefaultFont", int(min(tile_width, tile_height) * 1),"bold")
			)
			
			self.dropped_items.append(item)
			self.tag_raise(item)
		
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
		
class TradeNotebook(CustomNotebook):
	def __init__(self, parent, root, building):
		super().__init__(parent)
		
		self.parent = parent
		self.root = root
		self.building = building
		
		self.tabs = {
			"Buy": BuyItemTab(self),
			"Sell": SellItemTab(self),
		}
		
		self.init_tabs()
		
	def update_tabs(self):
		self.parent.update_popup()
		
		for tab in self.tabs.values():
			tab.update_tab()
		
class BuyItemTab(Tab):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.trade_nb = parent
		self.root = parent.root
		self.game = self.root.play_screen.game
		self.player = self.game.player
		self.settlement = parent.building.settlement
		
		self.grid = TradeGrid(self, self.settlement.sub_economy, self.game)
		self.grid.pack(fill=BOTH, expand=1)
		
		ttk.Button(self, text="Buy Item", command=self.buy_item).pack(fill=X)
		
	def buy_item(self):
		item_id = self.grid.get_selected_item()
		
		if item_id is None:
			return
			
		success = self.game.buy_item(self.player, self.settlement, item_id)
		
		if success:
			self.trade_nb.update_tabs()
			
	def update_tab(self):
		self.grid.populate_items()
		
class SellItemTab(Tab):
	def __init__(self, parent):
		super().__init__(parent)

		self.trade_nb = parent
		self.root = parent.root
		self.game = self.root.play_screen.game
		self.player = self.game.player
		self.settlement = parent.building.settlement

		self.grid = PlayerInventoryGrid(
			self,
			self.player,
			self.game,
			self.settlement,
		)
		self.grid.pack(fill=BOTH, expand=1)

		ttk.Button(
			self,
			text="Sell Item",
			command=self.sell_item
		).pack(fill=X)

	def sell_item(self):
		item_id = self.grid.get_selected_item()

		if item_id is None:
			return

		success = self.game.sell_item(
			self.player,
			self.settlement,
			item_id
		)

		if success:
			self.trade_nb.update_tabs()

	def update_tab(self):
		self.grid.populate_items()
		
class TradeGrid(ttk.Treeview):
	def __init__(self, parent, sub_economy, game):
		super().__init__(parent)
		
		columns = ("item", "quantity", "price", "creator")
		
		super().__init__(parent, columns=columns, show="headings")
		
		self.sub_economy = sub_economy
		self.game = game
		
		self.heading("item", text="Item")
		self.heading("quantity", text="Quantity")
		self.heading("price", text="Price")
		self.heading("creator", text="Creator")
		
		for col in columns:
			self.column(col, width=120, anchor="center", stretch=True)
			
		self.populate_items()
		
	def populate_items(self):
		for row in self.get_children():
			self.delete(row)
			
		inventory = getattr(self.sub_economy, "inventory", {})
		
		for item_type_id, quantity in inventory.items():
			if quantity <= 0:
				continue
				
			item_type = self.game.item_type_objs[item_type_id]
			price = self.sub_economy.get_value(item_type_id)
			
	
			self.insert(
				"",
				"end",
				iid=item_type_id,
				values=(
					item_type.name,
					quantity,
					price,
					item_type.creator,
				),
			)
			
	def get_selected_item(self):
		selected = self.selection()
		
		if not selected:
			return None
			
		return selected[0]
		
class PlayerInventoryGrid(ttk.Treeview):
	def __init__(self, parent, player, game, settlement):
		columns = ("item", "quantity", "price")
		
		super().__init__(parent, columns=columns, show="headings")
		
		self.player = player
		self.game = game
		self.settlement = settlement
		
		self.heading("item", text="Item")
		self.heading("quantity", text="Quantity")
		self.heading("price", text="Price")
		
		for col in columns:
			self.column(col, width=120, anchor="center", stretch=True)
			
		self.populate_items()
		
	def populate_items(self):
		for row in self.get_children():
			self.delete(row)
			
		for item_type_id, quantity in self.player.inventory.get_items():
			if quantity <= 0:
				continue
				
			item_type = self.game.item_type_objs[item_type_id]
			price = self.settlement.sub_economy.get_value(item_type_id)
			
			self.insert(
				"",
				"end",
				iid=item_type_id,
				values=(
					item_type.name,
					quantity,
					price,
				),
			)
			
	def get_selected_item(self):
		selected = self.selection()
		
		if not selected:
			return None
			
		return selected[0]		
		
class ProgressBar(Canvas):
	def __init__(self, parent, value=100, max_value=100, fill_color="green", text=None):
		super().__init__(
			parent, 
			width=200, 
			height=20, 
			highlightbackground="black", 
			highlightthickness=2
		)
		
		self.value = value
		
		self.max_value = max_value
		
		self.fill_color = fill_color
		
		self.fill_rect = None
		
		self.text = text
		
		self.bind("<Configure>", self.redraw)
		
	def redraw(self, event=None):
		self.delete("all")
		
		width = self.winfo_width()
		height = self.winfo_height()
		
		progress = min(self.value / self.max_value, 1.0)
		
		fill_width = int(width * progress)
		
		self.fill_rect = self.create_rectangle(0, 0, fill_width, height, fill=self.fill_color, width=0)
		
		if not self.text == None:
			self.create_text(
				width // 2,
				height // 2,
				text=self.text,
			)