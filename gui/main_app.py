# export PYTHONPATH=/home/yoavaviv/latent_explorer:$PYTHONPATH

# Python packages imports
import tkinter as tk
from tkinter import ttk

# Frontend imports
from gui.home_page import HomePage
from gui.new_play_page import PlayPage
from gui.explore_page import ExplorePage
from gui.get_started_page import GetStartedPage

class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Latent Explorer")

        # Set the window size to 800x600 pixels
        self.geometry("1300x600")

        # Create a style for the navigation buttons
        style = ttk.Style()
        style.configure('Nav.TButton', background='DeepSkyBlue4', foreground='white', font=('Helvetica', 10, 'bold'))

        # Navigation bar
        nav_bar = ttk.Frame(self, style='NavBar.TFrame')
        nav_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Styling the navigation bar
        style.configure('NavBar.TFrame', background='DeepSkyBlue4')

        # Navigation buttons
        ttk.Button(nav_bar, text="Home", style='Nav.TButton', command=lambda: self.show_frame(HomePage)).grid(row=0, column=0, sticky="ew", pady=50, padx=100)
        ttk.Button(nav_bar, text="Play", style='Nav.TButton', command=lambda: self.show_frame(PlayPage)).grid(row=2, column=0, sticky="ew", pady=10, padx=100)
        ttk.Button(nav_bar, text="Explore", style='Nav.TButton', command=lambda: self.show_frame(ExplorePage)).grid(row=3, column=0, sticky="ew", pady=10, padx=100)
        ttk.Button(nav_bar, text="Get Started", style='Nav.TButton', command=lambda: self.show_frame(GetStartedPage)).grid(row=4, column=0, sticky="ew", pady=10, padx=100)
        ttk.Button(nav_bar, text="Settings", style='Nav.TButton', command=lambda: self.show_frame(GetStartedPage)).grid(row=5, column=0, sticky="ew", pady=10, padx=100)
        # Make the nav_bar expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)  # New column for sidebar
        self.grid_columnconfigure(2, weight=1)  # Main content column

        # Main content area
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=2, sticky="nsew", padx=2)

        self.frames = {}
        for F in (HomePage, PlayPage, ExplorePage, GetStartedPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()