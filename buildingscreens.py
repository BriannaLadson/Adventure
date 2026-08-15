from tkinter import *
from tkinter import ttk

from screenwidgets import Popup, CustomNotebook, Tab

#BankPopup
class BankPopup(Popup):
	def __init__(self, root, building):
		super().__init__(root)
		
		self.play_screen = play_screen = None
		
		if hasattr(root, "play_screen"):
			self.play_screen = play_screen = root.play_screen
			
		self.game = game = self.play_screen.game
		self.player = player = game.player
			
		self.building = building
		
		self.settlement = settlement = building.settlement
		
		ttk.Label(self, text=f"Bank of {settlement.civilization.name}", anchor="center").pack(fill=X)
		
		self.bank_notebook = BankNotebook(self)
		self.bank_notebook.pack(fill=BOTH, expand=1)
		
		ttk.Button(self, text="OK", command=self.close).pack(fill=X)
		
		self.center()
		
	def close(self):
		if self.play_screen is not None:
			self.play_screen.can_process_input = True
			
		self.destroy()
		
class BankNotebook(CustomNotebook):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.bank_popup = parent
		
		self.tabs = {
			"Bank": BankTab(self),
			"Checking": CheckingTab(self),
		}
		
		self.init_tabs()
		
	def update_tabs(self):
		for tab in self.tabs.values():
			if hasattr(tab, "update_tab"):
				tab.update_tab()
		
class BankTab(Tab):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.bank_notebook = parent
		self.bank_popup = parent.bank_popup
		
		exchange_currency_btn = ttk.Button(self, text="Exchange Currency", command=self.exchange_currency)
		exchange_currency_btn.pack(fill=X)
		
	def exchange_currency(self):
		ExchangeCurrencyPopup(self.bank_popup, self.bank_notebook)
		
class CheckingTab(Tab):
	def __init__(self, parent):
		super().__init__(parent)

		self.bank_popup = parent.bank_popup

		self.game = self.bank_popup.game
		self.player = self.bank_popup.player
		self.settlement = self.bank_popup.settlement
		self.bank = self.settlement.bank

		self.update_tab()

	def update_tab(self):
		for widget in self.winfo_children():
			widget.destroy()

		if self.bank.has_checking_account(self.player):
			self.show_account()

		else:
			self.show_open_account()
			
		self.bank_popup.center()
			
	def show_open_account(self):
		currency_id = self.bank.get_currency()
		currency = self.game.coin_objs[currency_id]

		minimum = self.bank.minimum_checking_deposit

		ttk.Label(
			self,
			text="Checking Account",
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text=f"Minimum Opening Deposit: {minimum} {currency.name}",
			anchor="center",
		).pack(fill=X)

		wallet_quantity = self.player.wallet.get_quantity(
			currency_id
		)

		ttk.Label(
			self,
			text=f"You Have: {wallet_quantity} {currency.name}",
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text="Opening Deposit",
			anchor="center",
		).pack(fill=X)

		self.open_amount_var = StringVar(
			value=str(minimum)
		)

		ttk.Entry(
			self,
			textvariable=self.open_amount_var,
		).pack(fill=X)

		ttk.Button(
			self,
			text="Open Account",
			command=self.open_account,
		).pack(fill=X)
		
	def open_account(self):
		try:
			amount = int(self.open_amount_var.get())

		except ValueError:
			return

		success = self.bank.open_checking_account(
			self.game,
			self.player,
			amount,
		)

		if success:
			self.update_tab()
			
	def show_account(self):
		currency_id = self.bank.get_currency()
		currency = self.game.coin_objs[currency_id]

		balance = self.bank.get_checking_balance(
			self.player
		)

		wallet_quantity = self.player.wallet.get_quantity(
			currency_id
		)

		ttk.Label(
			self,
			text="Checking Account",
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text=f"Balance: {balance} {currency.name}",
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text=f"Wallet: {wallet_quantity} {currency.name}",
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text="Amount",
			anchor="center",
		).pack(fill=X)

		self.amount_var = StringVar(value="1")

		ttk.Entry(
			self,
			textvariable=self.amount_var,
		).pack(fill=X)

		ttk.Button(
			self,
			text="Deposit",
			command=self.deposit,
		).pack(fill=X)

		ttk.Button(
			self,
			text="Withdraw",
			command=self.withdraw,
		).pack(fill=X)

		ttk.Button(
			self,
			text="Close Account",
			command=self.close_account,
		).pack(fill=X)
		
	def get_amount(self):
		try:
			return int(self.amount_var.get())

		except ValueError:
			return None

	def deposit(self):
		amount = self.get_amount()

		if amount is None:
			return

		success = self.bank.deposit_checking(
			self.game,
			self.player,
			amount,
		)

		if success:
			self.update_tab()

	def withdraw(self):
		amount = self.get_amount()

		if amount is None:
			return

		success = self.bank.withdraw_checking(
			self.game,
			self.player,
			amount,
		)

		if success:
			self.update_tab()

	def close_account(self):
		success = self.bank.close_checking_account(
			self.game,
			self.player,
		)

		if success:
			self.update_tab()

#ExchangeCurrencyPopup
class ExchangeCurrencyPopup(Popup):
	def __init__(self, root, bank_notebook):
		super().__init__(root)
		
		self.bank_notebook = bank_notebook

		self.game = game = root.game
		self.player = player = root.player
		self.settlement = settlement = root.settlement
		self.bank = bank = settlement.bank

		self.target_coin_id = target_coin_id = bank.get_currency()
		self.target_coin = target_coin = game.coin_objs[target_coin_id]

		ttk.Label(
			self,
			text="Exchange Currency",
			anchor="center",
		).pack(fill=X)

		self.currency_options = {}

		for coin_id, quantity in player.wallet.get_coins():
			if coin_id == target_coin_id:
				continue

			if quantity < 1:
				continue

			coin = game.coin_objs[coin_id]

			self.currency_options[coin.name] = coin_id

		if not self.currency_options:
			ttk.Label(
				self,
				text="You have no foreign currency to exchange.",
				anchor="center",
			).pack(fill=X)

			ttk.Button(
				self,
				text="OK",
				command=self.destroy,
			).pack(fill=X)

			self.center()
			return

		ttk.Label(
			self,
			text="Currency",
			anchor="center",
		).pack(fill=X)

		self.currency_var = StringVar(
			value=list(self.currency_options.keys())[0]
		)

		self.currency_cbx = ttk.Combobox(
			self,
			textvariable=self.currency_var,
			values=list(self.currency_options.keys()),
			state="readonly",
		)
		self.currency_cbx.pack(fill=X)

		self.currency_cbx.bind(
			"<<ComboboxSelected>>",
			self.update_quote,
		)

		self.wallet_quantity_var = StringVar()

		ttk.Label(
			self,
			textvariable=self.wallet_quantity_var,
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			text="Amount",
			anchor="center",
		).pack(fill=X)

		self.quantity_var = StringVar(value="1")

		self.quantity_var.trace_add(
			"write",
			self.update_quote,
		)

		ttk.Entry(
			self,
			textvariable=self.quantity_var,
		).pack(fill=X)

		self.gross_var = StringVar()
		self.fee_var = StringVar()
		self.receive_var = StringVar()

		ttk.Label(
			self,
			textvariable=self.gross_var,
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			textvariable=self.fee_var,
			anchor="center",
		).pack(fill=X)

		ttk.Label(
			self,
			textvariable=self.receive_var,
			anchor="center",
		).pack(fill=X)

		self.ok_btn = ttk.Button(
			self,
			text="OK",
			command=self.confirm,
		)
		self.ok_btn.pack(fill=X)

		ttk.Button(
			self,
			text="Cancel",
			command=self.destroy,
		).pack(fill=X)

		self.update_quote()
		self.center()
		
	def get_selected_currency_id(self):
		currency_name = self.currency_var.get()

		return self.currency_options[currency_name]

	def update_quote(self, *args):
		source_coin_id = self.get_selected_currency_id()

		source_coin = self.game.coin_objs[source_coin_id]

		wallet_quantity = self.player.wallet.get_quantity(
			source_coin_id
		)

		self.wallet_quantity_var.set(
			f"You Have: {wallet_quantity} {source_coin.name}"
		)

		try:
			quantity = int(self.quantity_var.get())

		except ValueError:
			self.clear_quote()
			return

		if quantity <= 0 or quantity > wallet_quantity:
			self.clear_quote()
			return

		quote = self.bank.get_exchange_quote(
			self.game,
			source_coin_id,
			quantity,
		)

		if quote is None:
			self.clear_quote()
			return

		gross_quantity, fee_quantity, net_quantity = quote

		target_name = self.target_coin.name

		self.gross_var.set(
			f"Exchange Value: {gross_quantity} {target_name}"
		)

		self.fee_var.set(
			f"Service Fee ({self.bank.exchange_fee}%): "
			f"{fee_quantity} {target_name}"
		)

		self.receive_var.set(
			f"You Receive: {net_quantity} {target_name}"
		)

		if net_quantity <= 0:
			self.ok_btn.config(state=DISABLED)
			return

		if not self.bank.wallet.has_coins(
			self.target_coin_id,
			net_quantity,
		):
			self.receive_var.set(
				"Bank does not have enough currency."
			)

			self.ok_btn.config(state=DISABLED)
			return

		self.ok_btn.config(state=NORMAL)
		
		self.center()

	def clear_quote(self):
		self.gross_var.set("")
		self.fee_var.set("")
		self.receive_var.set("")

		self.ok_btn.config(state=DISABLED)

	def confirm(self):
		source_coin_id = self.get_selected_currency_id()

		try:
			quantity = int(self.quantity_var.get())

		except ValueError:
			return

		success = self.bank.exchange_currency(
			self.game,
			self.player,
			source_coin_id,
			quantity,
		)

		if success:
			self.bank_notebook.update_tabs()
			self.destroy()
			
			

#TradePopup
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
		selected = self.selection()

		selected_item = None

		if selected:
			selected_item = selected[0]

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

		if selected_item is not None:
			if self.exists(selected_item):
				self.selection_set(selected_item)
				self.focus(selected_item)
				
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
		selected = self.selection()

		selected_item = None

		if selected:
			selected_item = selected[0]

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

		if selected_item is not None:
			if self.exists(selected_item):
				self.selection_set(selected_item)
				self.focus(selected_item)
			
	def get_selected_item(self):
		selected = self.selection()
		
		if not selected:
			return None
			
		return selected[0]		