from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip

import helpfunctions as helpf

#Custom Notebooks
class CustomNotebook(ttk.Notebook):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.tabs = {}
		
	def init_tabs(self):
		for tab_name, tab in self.tabs.items():
			self.add(tab, text=tab_name)
			
class CharacterCreationNotebook(CustomNotebook):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.screen = screen = parent
		
		self.tabs = {
			"Identity": CharacterCreationIdentityTab(self, screen),
			"Items": CharacterCreationItemsTab(self, screen),
			"Start": CharacterCreationStartTab(self, screen),
		}
		
		self.init_tabs()

class CharacterSheetNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Identity": CharacterSheetIdentityTab(self, game),
			"Crafting": CraftingTab(self, game),
			"Health": HealthNotebook(self, game),
			"Inventory": InventoryTab(self, game),
			"Memory": MemoryNotebook(self, game),
			"Stats":StatsTab(self, game),
		}
		
		self.init_tabs()
		
class HealthNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		
		self.tabs = {
			"Needs": NeedsTab(self, game)
		}
		
		self.init_tabs()
		
class MemoryNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Locations": LocationsTab(self, game),
		}
		
		self.init_tabs()
		
class InventoryNotebook(CustomNotebook):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.tabs = {
			"Items": ItemsTab(self, game),
			"Wallet": WalletTab(self, game),
		}
		
		self.init_tabs()

#Misc.
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

#Tabs	
class Tab(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		
class CharacterCreationIdentityTab(Tab):
	def __init__(self, parent, screen):
		super().__init__(parent)
		
		self.screen = screen
		
		self.game = screen.game
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		scr_fr = self.scrollable_frame.scrolling_frame
		
		#Race
		race_fr = ttk.Frame(scr_fr)
		race_fr.pack(pady=5)
		
		race_lbl = ttk.Label(race_fr, text="Race", anchor="center")
		race_lbl.pack()
		
		self.race_options = screen.race_options = {
			race.name: race for race in self.game.race_objs.values()
		}
		
		self.race_var = screen.race_var = StringVar(value=list(self.race_options.keys())[0])
		
		race_cbx = ttk.Combobox(race_fr, textvariable=self.race_var, values=list(self.race_options.keys()), state="readonly")
		race_cbx.pack()
		
class CharacterCreationItemsTab(Tab):
	def __init__(self, parent, screen):
		super().__init__(parent)
		
		self.screen = screen
		
		self.game = screen.game
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		scr_fr = self.scrollable_frame.scrolling_frame
		
		#Starting Currency
		start_currency_fr = ttk.Frame(scr_fr)
		start_currency_fr.pack(pady=5)
		
		start_currency_lbl = ttk.Label(start_currency_fr, text="Starting Currency", anchor="center")
		start_currency_lbl.grid(row=0, column=0, columnspan=2, sticky="we")
		
		self.currency_options = screen.currency_options = {
			currency.name: currency for currency in self.game.coin_objs.values()
		}
		
		self.currency_var = screen.currency_var = StringVar(value=list(self.currency_options.keys())[0])
		
		currency_cbx = ttk.Combobox(start_currency_fr, textvariable=self.currency_var, values=list(self.currency_options.keys()), state="readonly")
		currency_cbx.grid(row=1, column=0, padx=5)
		
		self.currency_quantity_var = screen.currency_quantity_var = StringVar(value=100)
		
		currency_quantity_ent = ttk.Entry(start_currency_fr, textvariable=self.currency_quantity_var)
		currency_quantity_ent.grid(row=1, column=1)
		
class CharacterCreationStartTab(Tab):
	def __init__(self, parent, screen):
		super().__init__(parent)
		
		self.screen = screen
		
		self.game = screen.game
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		scr_fr = self.scrollable_frame.scrolling_frame
		
		#Starting Location
		start_loc_fr = ttk.Frame(scr_fr)
		start_loc_fr.pack(pady=5)
		
		start_loc_lbl = ttk.Label(start_loc_fr, text="Starting Location", anchor="center")
		start_loc_lbl.pack()
		
		self.start_loc_var = screen.start_loc_var = StringVar(value="Random")
		self.start_loc_var.trace_add("write", screen.trace)
		
		start_loc_cbx = ttk.Combobox(start_loc_fr, textvariable=self.start_loc_var, values=["Random", "Random Settlement"], state="readonly")
		start_loc_cbx.pack()
		
class CharacterSheetIdentityTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = game.player
		
		self.scrollable_frame = ScrollableFrame(self)
		self.scrollable_frame.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		scr_fr = self.scrollable_frame.scrolling_frame
		helpf.destroy_children_widgets(scr_fr)
		
		ancestry = sorted(
			self.player.ancestry.items(),
			key=lambda entry: entry[1],
			reverse=True,
		)
		
		for race_id, ratio in ancestry:
			race = self.game.race_objs[race_id]
			percentage = f"{ratio * 100:.2f}".rstrip("0").rstrip(".")
			
			row_fr = ttk.Frame(scr_fr)
			row_fr.pack(fill=X)
			
			ttk.Label(row_fr, text=race.name, anchor="center").pack(side=LEFT)
			
			ttk.Label(row_fr, text=f"{percentage}%", anchor="center").pack(side=LEFT)
		
class CraftingTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)

		self.notebook = parent
		self.game = game
		self.player = game.player

		self.skill_options = {"All": None}

		skill_ids = {
			reaction.skill
			for reaction in game.crafting_reaction_objs.values()
			if reaction.skill is not None
		}

		for skill_id in sorted(skill_ids):
			self.skill_options[game.skills[skill_id]] = skill_id

		self.skill_var = StringVar(value="All")

		ttk.Label(self, text="Skill").pack(fill=X)

		self.skill_cbx = ttk.Combobox(
			self,
			textvariable=self.skill_var,
			values=list(self.skill_options),
			state="readonly",
		)
		self.skill_cbx.pack(fill=X)

		self.skill_cbx.bind(
			"<<ComboboxSelected>>",
			self.update_recipes,
		)
		
		self.map_btn = ttk.Button(
			self,
			text="Draw Map",
			command=self.open_map_crafting,
		)
		self.map_btn.pack(fill=X, padx=5, pady=2)

		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=True)
		
		self.recipe_buttons = {}
		self.recipe_tooltips = {}

		self.update_recipes()
		
		self.bind("<Visibility>", self.update_recipes)

	def get_quantity(self, item_id):
		if item_id in self.game.coin_objs:
			return self.player.wallet.get_quantity(item_id)

		return self.player.inventory.get_quantity(item_id)

	def can_craft(self, reaction):
		if reaction.skill is not None:
			if reaction.skill not in self.player.skills:
				return False

		return all(
			self.get_quantity(item_id) >= quantity
			for item_id, quantity in reaction.reagents.items()
		)

	def update_recipes(self, event=None):
		frame = self.scrollable_fr.scrolling_frame
		skill_id = self.skill_options[self.skill_var.get()]

		for button in self.recipe_buttons.values():
			button.pack_forget()

		reactions = sorted(
			self.game.crafting_reaction_objs.values(),
			key=lambda reaction: reaction.name,
		)

		for reaction in reactions:
			if skill_id is not None and reaction.skill != skill_id:
				continue

			if reaction.id not in self.recipe_buttons:
				button = ttk.Button(
					frame,
					text=reaction.name,
					command=lambda reaction_id=reaction.id: self.craft(
						reaction_id
					),
				)

				tooltip = ToolTip(
					button,
					msg=lambda reaction_id=reaction.id: (
						self.get_recipe_tooltip(reaction_id)
					),
					delay=0.4,
					follow=False,
					refresh=1.0,
					justify=LEFT,
					width=350,
				)

				self.recipe_buttons[reaction.id] = button
				self.recipe_tooltips[reaction.id] = tooltip

			button = self.recipe_buttons[reaction.id]

			button.config(
				state=NORMAL if self.can_craft(reaction) else DISABLED
			)
			button.pack(fill=X, padx=5, pady=2)

	def get_recipe_tooltip(self, reaction_id):
		reaction = self.game.crafting_reaction_objs[reaction_id]

		lines = [reaction.name]

		if reaction.skill is not None:
			skill_name = self.game.skills[reaction.skill]
			lines.append(f"Skill: {skill_name}")

		lines.extend(["", "Requires:"])

		for item_id, quantity in reaction.reagents.items():
			item = self.game.item_type_objs[item_id]
			available = self.get_quantity(item_id)

			lines.append(
				f"{item.name}: {available} / {quantity}"
			)

		lines.extend(["", "Produces:"])

		for item_id, quantity in reaction.products.items():
			item = self.game.item_type_objs[item_id]
			lines.append(f"{item.name} x{quantity}")

		lines.extend([
			"",
			f"Time: {reaction.ticks} tick(s)",
		])

		return "\n".join(lines)

	def craft(self, reaction_id):
		success, dead_entities = self.game.craft_reaction(
			self.player,
			reaction_id,
		)

		self.finish_crafting(success, dead_entities)
		
	def open_map_crafting(self):
		from popups import MapCraftingPopup

		MapCraftingPopup(
			self.winfo_toplevel(),
			self.game,
			self.finish_crafting,
		)

	def finish_crafting(self, success, dead_entities):
		popup = self.winfo_toplevel()
		play_screen = popup.root.play_screen

		if self.player in dead_entities:
			popup.destroy()
			play_screen.update_screen()
			play_screen.handle_player_death()
			return

		self.update_recipes()

		tabs = self.notebook.tabs

		inventory_tab = tabs["Inventory"]
		inventory_tabs = inventory_tab.inventory_notebook.tabs

		inventory_tabs["Items"].populate()
		inventory_tabs["Wallet"].populate()

		bar = inventory_tab.encumbrance_bar
		bar.value = self.player.cur_encumbrance
		bar.max_value = self.player.max_encumbrance
		bar.text = (
			f"Encumbrance: {self.player.cur_encumbrance}"
			f" / {self.player.max_encumbrance}"
		)
		bar.redraw()

		tabs["Health"].tabs["Needs"].populate()
		tabs["Stats"].populate()

		play_screen.update_screen()
			
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
			need = self.player.need_definitions[need_id]
			max_value = need["max"]
			
			bar = ProgressBar(
				scr_fr, 
				value=value, 
				max_value=max_value, 
				text=f"{need_id.capitalize()}: {value} / {max_value}"
			)
			bar.pack(pady=5)
			
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
			
class InventoryTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = player = game.player
		
		self.encumbrance_bar = ProgressBar(
			self,
			value=player.cur_encumbrance,
			max_value = player.max_encumbrance,
			text=f"Encumbrance: {player.cur_encumbrance} / {player.max_encumbrance}"
		)
		self.encumbrance_bar.pack(pady=5)
		
		self.inventory_notebook = InventoryNotebook(self, game)
		self.inventory_notebook.pack(fill=BOTH, expand=1)
		
class ItemsTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = player = game.player
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		from popups import ItemPopup
		
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
					source="inventory",
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
		from popups import ItemPopup
		
		game = self.game
		player = self.player
		wallet = player.wallet
		scr_fr = self.scrollable_fr.scrolling_frame
		
		helpf.destroy_children_widgets(scr_fr)
		
		for coin_id, quantity in wallet.get_coins():
			coin = game.coin_objs[coin_id]
			
			btn = ttk.Button(
				scr_fr,
				text=f"{coin.name} x{quantity}",
				command=lambda coin_id=coin_id, quantity=quantity: ItemPopup(
					self.winfo_toplevel(),
					game,
					coin_id,
					quantity,
					parent_tab=self,
					source="wallet",
				),
			)
			btn.pack(fill=X)

class StatsTab(Tab):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game
		self.player = game.player
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.populate()
		
	def populate(self):
		scr_fr = self.scrollable_fr.scrolling_frame
		helpf.destroy_children_widgets(scr_fr)
		player = self.player
		
		for skill, skill_data in player.skills.items():
			skill_name = skill_data["name"]
			level = skill_data["level"]
			value = skill_data["xp"]
			max_value = skill_data["max_xp"]
		
		
			bar = ProgressBar(
				scr_fr,
				value=value,
				max_value=max_value,
				text=f"{skill_name.capitalize()} - Level {level}: {value} / {max_value}"
			)
			bar.pack(pady=5)