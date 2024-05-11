# Python packages
import tkinter as tk
import os
from tkinter import ttk, filedialog

# API imports
from api.explore.calc_inversion import calc_inversiones

# Frontend imports
from gui.home_page import HomePage

class ExplorePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.dataset_dir = None  # Variable to store the selected directory path

        ttk.Button(self, text="Choose Dataset Dir", command=self.choose_dataset_dir).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(self, text="Calculate Embeddings", command=self.calc_inversions).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(self, text="Go Home", command=lambda: controller.show_frame(HomePage)).grid(row=0, column=2, padx=10, pady=10)

    def choose_dataset_dir(self):
        self.dataset_dir = filedialog.askdirectory()
        if self.dataset_dir:
            print("Selected folder:", self.dataset_dir)  # Optional: for confirmation

            # Determine the parent directory of the chosen directory
            parent_dir = os.path.dirname(self.dataset_dir)

            # Define the paths for the new directories
            self.processed_images_dir = os.path.join(parent_dir, "processed_images")
            self.embeddings_dir = os.path.join(parent_dir, "embeddings")

            # Check if these directories exist, and create them if they don't
            for dir_path in [self.processed_images_dir, self.embeddings_dir]:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    print(f"Created directory: {dir_path}")
                else:
                    print(f"Directory already exists: {dir_path}")

    def calc_inversions(self):
        calc_inversiones(input_images_dir=self.dataset_dir, processed_images_dir=self.processed_images_dir, embbeding_images_dir=self.embeddings_dir)
