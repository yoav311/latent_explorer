from tkinter import ttk
import tkinter.font as tkFont

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        # Create a bold font for the title and first words
        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        regular_font = tkFont.Font(family="Helvetica", size=12)

         # Title
        ttk.Label(self, text="Welcome to the Latent Explorer App!", font=title_font).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Spacing rows for gaps
        self.grid_rowconfigure(1, weight=1, minsize=80)  # Gap after title
        self.grid_rowconfigure(2, weight=1)  # First label row
        self.grid_rowconfigure(3, weight=1, minsize=80)  # Gap between first and second label
        self.grid_rowconfigure(4, weight=1)  # Second label row
        self.grid_rowconfigure(5, weight=1, minsize=80)  # Gap between second and third label
        self.grid_rowconfigure(6, weight=1)  # Third label row

        # First text label
        ttk.Label(self, text="Play", font=bold_font).grid(row=2, column=0, sticky="e")
        ttk.Label(self, text="with the latent spaces of your own images and generate new image with costume latent directions.", font=regular_font).grid(row=2, column=1, sticky="w")

        # Second text label
        ttk.Label(self, text="Explore", font=bold_font).grid(row=4, column=0, sticky="e")
        ttk.Label(self, text="new directions in the human images latent space by training your own SVM on a costume dataset", font=regular_font).grid(row=4, column=1, sticky="w")

        # Third text label
        ttk.Label(self, text="Get-Started", font=bold_font).grid(row=6, column=0, sticky="e")
        ttk.Label(self, text="with all the pre request installations and settings for a smooth executions", font=regular_font).grid(row=6, column=1, sticky="w")
