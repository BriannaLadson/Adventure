from tkinter import *

import screens
import helpfunctions as helpf

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.title("Adventure")
		self.state("zoomed")
		
if __name__ == "__main__":
	helpf.create_dir("saves/")
	
	root = Root()
	
	root.start_screen = screens.StartScreen(root)
	root.start_screen.pack(fill=BOTH, expand=1)
	
	root.mainloop()