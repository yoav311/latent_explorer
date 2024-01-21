from tkinter import ttk

# Frontend imports
from gui.home_page import HomePage

class GetStartedPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        ttk.Button(self, text="Go Home", command=lambda: controller.show_frame(HomePage)).grid(row=0, column=0, padx=10, pady=10)
