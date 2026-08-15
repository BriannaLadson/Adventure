import random

from entities import Wallet

class Bank:
	def __init__(self, settlement=None, use_settlement_wallet=True):
		self.settlement = settlement
		
		if settlement is not None and use_settlement_wallet:
			self.wallet = settlement.wallet
			
		else:
			self.wallet = Wallet()
		
		self.exchange_fee = random.randint(1, 10)
		
		self.minimum_checking_deposit = random.randint(1, 100)
		
		self.checking_accounts = {}
		
	def get_currency(self):
		if self.settlement is None:
			return None
			
		return self.settlement.currency
		
	def get_currency_value(self, game, coin_id):
		coin = game.coin_objs[coin_id]

		value = 0

		for reagent_id, quantity in coin.reagents.items():
			if reagent_id not in game.bar_objs:
				continue

			bar = game.bar_objs[reagent_id]
			value += bar.base_value * quantity

		return value
		
	def get_exchange_quote(self, game, source_coin_id, quantity):
		target_coin_id = self.get_currency()

		if target_coin_id is None:
			return None

		source_value = self.get_currency_value(
			game,
			source_coin_id,
		)

		target_value = self.get_currency_value(
			game,
			target_coin_id,
		)

		if source_value <= 0 or target_value <= 0:
			return None

		total_value = source_value * quantity

		gross_quantity = int(total_value / target_value)

		fee_quantity = max(1, int(gross_quantity * (self.exchange_fee / 100)))

		net_quantity = gross_quantity - fee_quantity

		return gross_quantity, fee_quantity, net_quantity
		
	def exchange_currency(self, game, character, source_coin_id, quantity):
		if quantity <= 0:
			return False

		target_coin_id = self.get_currency()

		if target_coin_id is None:
			return False

		if source_coin_id == target_coin_id:
			return False

		quote = self.get_exchange_quote(
			game,
			source_coin_id,
			quantity,
		)

		if quote is None:
			return False

		gross_quantity, fee_quantity, net_quantity = quote

		if net_quantity <= 0:
			return False

		if not character.wallet.has_coins(
			source_coin_id,
			quantity,
		):
			return False

		if not self.wallet.has_coins(
			target_coin_id,
			net_quantity,
		):
			return False

		removed = character.remove_carried_object(
			source_coin_id,
			game,
			quantity,
		)

		if not removed:
			return False

		self.wallet.add_coins(
			source_coin_id,
			quantity,
		)

		self.wallet.remove_coins(
			target_coin_id,
			net_quantity,
		)

		character.add_carried_object(
			target_coin_id,
			game,
			net_quantity,
		)

		return True
		
	def has_checking_account(self, character):
		return character in self.checking_accounts
		
	def get_checking_balance(self, character):
		return self.checking_accounts.get(character, 0)
		
	def open_checking_account(self, game, character, amount):
		if self.has_checking_account(character):
			return False
			
		if amount < self.minimum_checking_deposit:
			return False
			
		currency = self.get_currency()
		
		if currency is None:
			return False
			
		if not character.wallet.has_coins(currency, amount):
			return False
			
		removed = character.remove_carried_object(currency, game, amount)
		
		if not removed:
			return False
			
		self.wallet.add_coins(currency, amount)
		
		self.checking_accounts[character] = amount
		
		return True
		
	def deposit_checking(self, game, character, amount):
		if not self.has_checking_account(character):
			return False

		if amount <= 0:
			return False

		currency = self.get_currency()

		if currency is None:
			return False

		if not character.wallet.has_coins(
			currency,
			amount,
		):
			return False

		removed = character.remove_carried_object(
			currency,
			game,
			amount,
		)

		if not removed:
			return False

		self.wallet.add_coins(
			currency,
			amount,
		)

		self.checking_accounts[character] += amount

		return True
		
	def withdraw_checking(self, game, character, amount):
		if not self.has_checking_account(character):
			return False

		if amount <= 0:
			return False

		if self.get_checking_balance(character) < amount:
			return False

		currency = self.get_currency()

		if currency is None:
			return False

		if not self.wallet.has_coins(
			currency,
			amount,
		):
			return False

		removed = self.wallet.remove_coins(
			currency,
			amount,
		)

		if not removed:
			return False

		self.checking_accounts[character] -= amount

		character.add_carried_object(
			currency,
			game,
			amount,
		)

		return True
		
	def close_checking_account(self, game, character):
		if not self.has_checking_account(character):
			return False

		balance = self.get_checking_balance(character)

		currency = self.get_currency()

		if currency is None:
			return False

		if balance > 0:
			if not self.wallet.has_coins(
				currency,
				balance,
			):
				return False

			removed = self.wallet.remove_coins(
				currency,
				balance,
			)

			if not removed:
				return False

			character.add_carried_object(
				currency,
				game,
				balance,
			)

		del self.checking_accounts[character]

		return True