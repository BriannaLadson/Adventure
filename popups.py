from tkinter import *
from tkinter import ttk
import os

import helpfunctions as helpf
import entities
import dataparsing
from screenwidgets import CharacterSheetNotebook, ScrollableFrame, ScrollableListbox

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
		
		tw = self.winfo_reqwidth()
		th = self.winfo_reqheight()
		
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
		from screens import WorldGenerationScreen
		
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
		from screens import WorldGenerationScreen
		
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
	def __init__(self, root, game, item_id, quantity=1, parent_tab=None, source="inventory"):
		super().__init__(root)
		
		self.parent_tab = parent_tab
		
		self.game = game
		self.item_id = item_id
		self.quantity = quantity
		self.source = source
		self.item = item = game.item_type_objs[item_id]
		
		ttk.Label(self, text=self.item.name, anchor="center").pack(fill=X)
		
		self.quantity_lbl = ttk.Label(self, text=f"Quantity: {quantity}", anchor="center")
		self.quantity_lbl.pack(fill=X)
		
		value = getattr(self.item, "value", getattr(self.item, "base_value", 0))
		ttk.Label(self, text=f"Base Value: {value}", anchor="center").pack(fill=X)
		
		ttk.Label(self, text=item.description, wraplength=300, anchor="center").pack(fill=BOTH, expand=1)
		
		# Needs
		player = game.player
		need_values = player.get_item_need_values(item_id, game)
		
		if need_values:
			for need_id, amount in need_values.items():
				sign = "+" if amount > 0 else ""
				
				ttk.Label(
					self,
					text=f"{need_id.capitalize()}: {sign}{amount}",
					anchor="center"
				).pack(fill=X)
			
		self.action_funcs = {
			"consume": self.consume_item,
			"drop": self.drop_item,
		}
		
		actions = list(getattr(item, "actions", []))
		
		if need_values:
			if "consume" not in actions:
				actions.append("consume")
				
		else:
			if "consume" in actions:
				actions.remove("consume")
		
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
		
		if not player.is_location_local():
			return
			
		if self.quantity > 1:
			DropQuantityPopup(
				self.root,
				self.item.name,
				self.quantity,
				self.perform_drop,
			)
			return
			
		self.perform_drop(1)
		
	def perform_drop(self, quantity):
		player = self.game.player

		success = player.drop_item(
			self.item_id,
			self.game,
			quantity=quantity,
			source=self.source,
		)

		if not success:
			return

		if self.parent_tab is not None:
			self.parent_tab.populate()
			
		self.root.root.play_screen.tile_map.update_map()

		self.quantity -= quantity

		if self.quantity <= 0:
			self.destroy()
			return

		self.quantity_lbl.config(
			text=f"Quantity: {self.quantity}"
		)
			
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
		from screens import CharacterCreationScreen
		
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
		from screens import StartScreen
		
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
		from screens import PlayScreen
		
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
	def __init__(
		self,
		root,
		game,
		first_inventory,
		second_inventory,
		first_inv_text="Inventory",
		second_inv_text="Inventory",
		first_is_character=False,
		second_is_character=False,
	):
		super().__init__(root)

		self.game = game

		self.first_inventory = first_inventory
		self.second_inventory = second_inventory

		self.first_is_character = first_is_character
		self.second_is_character = second_is_character

		top_fr = ttk.Frame(self)
		top_fr.pack(fill=BOTH, expand=1)

		self.first_inventory_fr = ttk.Frame(top_fr)
		self.first_inventory_fr.pack(side=LEFT, fill=Y)

		first_inventory_lbl = ttk.Label(
			self.first_inventory_fr,
			text=first_inv_text,
			anchor="center",
		)
		first_inventory_lbl.pack(fill=X)

		self.first_inventory_scr_fr = ScrollableFrame(
			self.first_inventory_fr
		)
		self.first_inventory_scr_fr.pack(
			fill=BOTH,
			expand=1,
		)

		self.first_inventory_btn = ttk.Button(
			self.first_inventory_fr,
			text="Transfer All",
			command=lambda: self.transfer_all(
				self.first_inventory,
				self.second_inventory,
				self.first_is_character,
				self.second_is_character,
			),
		)
		self.first_inventory_btn.pack(fill=X)

		self.second_inventory_fr = ttk.Frame(top_fr)
		self.second_inventory_fr.pack(side=LEFT, fill=Y)

		second_inventory_lbl = ttk.Label(
			self.second_inventory_fr,
			text=second_inv_text,
			anchor="center",
		)
		second_inventory_lbl.pack(fill=X)

		self.second_inventory_scr_fr = ScrollableFrame(
			self.second_inventory_fr
		)
		self.second_inventory_scr_fr.pack(
			fill=BOTH,
			expand=1,
		)

		self.second_inventory_btn = ttk.Button(
			self.second_inventory_fr,
			text="Transfer All",
			command=lambda: self.transfer_all(
				self.second_inventory,
				self.first_inventory,
				self.second_is_character,
				self.first_is_character,
			),
		)
		self.second_inventory_btn.pack(fill=X)

		self.close_btn = ttk.Button(
			self,
			text="Close",
			command=self.close,
		)
		self.close_btn.pack(fill=X)

		self.populate()

		self.center()

	def get_items(self, container, is_character):
		if is_character:
			items = list(container.inventory.get_items())

			for coin_id, quantity in container.wallet.get_coins():
				items.append((coin_id, quantity))

			return items

		return list(container.get_items())

	def add_object(self, container, is_character, item_id, quantity):
		if is_character:
			return container.add_carried_object(
				item_id,
				self.game,
				quantity,
			)
			
		self.root.play_screen.tile_map.update_map()

		return container.add_item(
			item_id,
			quantity,
		)

	def remove_object(
		self,
		container,
		is_character,
		item_id,
		quantity,
	):
		if is_character:
			return container.remove_carried_object(
				item_id,
				self.game,
				quantity,
			)
			
		self.root.play_screen.tile_map.update_map()

		return container.remove_item(
			item_id,
			quantity,
		)

	def populate_inventory(
		self,
		scroll_frame,
		source_container,
		target_container,
		source_is_character,
		target_is_character,
	):
		frame = scroll_frame.scrolling_frame

		for widget in frame.winfo_children():
			widget.destroy()

		for item_id, quantity in self.get_items(
			source_container,
			source_is_character,
		):
			item_frame = ttk.Frame(frame)
			item_frame.pack(fill=X)

			item = self.game.item_type_objs[item_id]

			ttk.Label(
				item_frame,
				text=f"{item.name} x{quantity}",
				anchor="center",
			).pack(
				side=LEFT,
				fill=X,
				expand=True,
			)

			ttk.Button(
				item_frame,
				text="Move",
				command=lambda i=item_id,
				s=source_container,
				t=target_container,
				s_char=source_is_character,
				t_char=target_is_character: self.move_item(
					s,
					t,
					i,
					1,
					s_char,
					t_char,
				),
			).pack(side=RIGHT)

			ttk.Button(
				item_frame,
				text="Move All",
				command=lambda i=item_id,
				q=quantity,
				s=source_container,
				t=target_container,
				s_char=source_is_character,
				t_char=target_is_character: self.move_item(
					s,
					t,
					i,
					q,
					s_char,
					t_char,
				),
			).pack(side=RIGHT)

	def move_item(
		self,
		source_container,
		target_container,
		item_id,
		quantity,
		source_is_character,
		target_is_character,
	):
		removed = self.remove_object(
			source_container,
			source_is_character,
			item_id,
			quantity,
		)

		if not removed:
			return

		added = self.add_object(
			target_container,
			target_is_character,
			item_id,
			quantity,
		)

		if not added:
			self.add_object(
				source_container,
				source_is_character,
				item_id,
				quantity,
			)

		self.populate()

	def transfer_all(
		self,
		source_container,
		target_container,
		source_is_character,
		target_is_character,
	):
		items = self.get_items(
			source_container,
			source_is_character,
		)

		for item_id, quantity in items:
			removed = self.remove_object(
				source_container,
				source_is_character,
				item_id,
				quantity,
			)

			if not removed:
				continue

			added = self.add_object(
				target_container,
				target_is_character,
				item_id,
				quantity,
			)

			if not added:
				self.add_object(
					source_container,
					source_is_character,
					item_id,
					quantity,
				)
				
		self.root.play_screen.tile_map.update_map()

		self.populate()

	def populate(self):
		self.populate_inventory(
			self.first_inventory_scr_fr,
			self.first_inventory,
			self.second_inventory,
			self.first_is_character,
			self.second_is_character,
		)

		self.populate_inventory(
			self.second_inventory_scr_fr,
			self.second_inventory,
			self.first_inventory,
			self.second_is_character,
			self.first_is_character,
		)

	def close(self):
		self.destroy()
		
class DropQuantityPopup(Popup):
	def __init__(self, root, item_name, max_quantity, callback):
		super().__init__(root)

		self.max_quantity = max_quantity
		self.callback = callback

		ttk.Label(
			self,
			text=f"Drop how many {item_name}?",
			anchor="center",
		).pack(fill=X)

		self.quantity_var = IntVar(value=1)

		self.quantity_spn = ttk.Spinbox(
			self,
			from_=1,
			to=max_quantity,
			textvariable=self.quantity_var,
		)
		self.quantity_spn.pack(fill=X, padx=5, pady=5)

		ttk.Button(
			self,
			text="Drop",
			command=self.confirm,
		).pack(fill=X)

		ttk.Button(
			self,
			text="Cancel",
			command=self.destroy,
		).pack(fill=X)

		self.center()

	def confirm(self):
		try:
			quantity = int(self.quantity_var.get())

		except (ValueError, TclError):
			return

		if quantity < 1 or quantity > self.max_quantity:
			return
			
		self.destroy()

		self.callback(quantity)