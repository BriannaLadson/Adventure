from tkinter import *

import screens
import helpfunctions as helpf

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.title("Adventure v0.10.1")
		self.state("zoomed")
		
if __name__ == "__main__":
	helpf.create_dir("saves")
	
	root = Root()
	
	root.start_screen = screens.StartScreen(root)
	root.start_screen.display()
	
	root.mainloop()