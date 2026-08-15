from tkinter import *
from tkinter import ttk

class CustomNotebook(ttk.Notebook):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.tabs = {}
		
	def init_tabs(self):
		for tab_name, tab in self.tabs.items():
			self.add(tab, text=tab_name)

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
		
class Tab(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)