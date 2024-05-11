import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import os
import torch
from PIL import Image, ImageTk
import os
import shutil
import dlib
from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageTk
import torch
import threading

# API imports
from api.image_processing.face_alignment import align_face
from api.configs import paths_config
from api.play import run_pti as pti_inversion

class DirectionWidget(ttk.Frame):
    def __init__(self, parent, directions, update_callback):
        super().__init__(parent)
        
        self.directions = directions
        self.update_callback = update_callback
        self.variable = tk.StringVar(self)
        self.variable.set("Select Direction")
        
        self.dropdown = ttk.Combobox(self, textvariable=self.variable, values=list(self.directions.keys()))
        self.dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        self.dropdown.bind('<<ComboboxSelected>>', self.on_direction_selected)
        
        self.scale_value_label = ttk.Label(self, text="Value: 0.0")  # Initial label text
        self.scale_value_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.scale = None

    def on_direction_selected(self, event):
        direction = self.variable.get()
        if self.scale:
            self.scale.destroy()
        self.scale = ttk.Scale(self, from_=-5, to=5, orient='horizontal', command=self.on_scale_change)
        self.scale.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        
    def on_scale_change(self, value):
        self.update_callback(self.variable.get(), float(value))
        self.scale_value_label.config(text=f"Value: {float(value):.1f}")  # Update label text


class PlayPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.direction_widgets = []

        # Initialize a counter for tracking the grid row for new widgets
        self.next_grid_row = 6  # Adjust the starting row as needed based on your layout
        self.add_direction_button = ttk.Button(self, text="Add Another Direction", command=self.add_direction_widget)
        # Place the button at a specific row, and update self.next_grid_row accordingly
        self.add_direction_button.grid(row=self.next_grid_row, column=4, sticky="nsew", padx=5, pady=5)
        self.next_grid_row += 1  # Increment for the next widget

        self.direction_tensors = self.load_direction_tensors('./database/editing_directions/interfacegan_directions/')

        self.upload_new_image_button = ttk.Button(self, text="Upload New Image", command=self.upload_image)
        self.upload_new_image_button.grid(row=2, column=4, padx=30, pady=10, sticky="ew")
        self.upload_existing_image_button = ttk.Button(self, text="Upload existing Inversion", command=self.upload_inverted_image)
        self.upload_existing_image_button.grid(row=2, column=5, padx=30, pady=10, sticky="ew")

        self.create_gan_inversion_button = ttk.Button(self, text="Create GAN Inversion -->", command=self.start_gan_inversion)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.waiting_massage = ttk.Label(self, text="It can take arround 1-2 minutes")
        self.original_image_label = ttk.Label(self, text="Original Image")
        self.edited_image_label = ttk.Label(self, text="Edited Image")
        self.image_on_window = False
        self.inversion_image_on_window = False

        self.generate_button = ttk.Button(self, text="Generate New Image", command=self.generate_new_image)
        self.save_button = ttk.Button(self, text="Save image", command=self.save_image)


    def upload_image(self):

        # Reset the edited image if exists
        self.edited_new_image = None

        self.create_gan_inversion_button.grid_remove()
        self.edited_image_label.grid_remove()
        self.original_image_label.grid_remove()
        self.generate_button.grid_remove()

        if self.image_on_window:
            self.original_img.grid_remove()
            self.image_on_window = False
        if self.inversion_image_on_window:
            self.new_img_label.grid_remove()
            self.inversion_image_on_window = False

        self.image_path = filedialog.askopenfilename()
        IMAGE_SIZE = 1024
        predictor = dlib.shape_predictor(paths_config.dlib)

        if self.image_path:
            pre_process_img = align_face(filepath=self.image_path, predictor=predictor, output_size=IMAGE_SIZE)
            path_without_ext = self.image_path.split('.')[0]
            self.processed_image_path = f'{path_without_ext}_processed.jpeg'
            print(f"saving_path: {self.processed_image_path}")
            pre_process_img.save(self.processed_image_path)

            img = Image.open(self.processed_image_path)
            img.thumbnail((250, 250))
            img = ImageTk.PhotoImage(img)
            self.original_img = ttk.Label(self, image=img)
            self.original_img.image = img
            self.original_img.grid(row=4, column=2, columnspan=2, padx=30, pady=10)
            self.original_image_label.grid(row=3, column=2, columnspan=2, padx=30, pady=10)
            self.image_on_window = True

            self.create_gan_inversion_button.grid(row=4, column=4, padx=30, pady=10, sticky="ew")
    
    def save_image(self):
        if self.edited_new_image is not None:
            image_name = simpledialog.askstring("Input", "Enter the image name:", parent=self)
            image_saving_path = os.path.join(self.user_root_folder, "output_images", f"{image_name}.jpeg")
            self.edited_new_image.save(image_saving_path)
        
    def get_file_path(self, folder_path, file_extention):
        # List all files in the directory
        files_in_directory = os.listdir(folder_path)

        files_with_desired_ext = [file for file in files_in_directory if file.endswith(file_extention)]

        # Get the path of the first image file
        if files_with_desired_ext:
            output_file_path = os.path.join(folder_path, files_with_desired_ext[0])
            return(output_file_path)
        else:
            return None

    def upload_inverted_image(self):

        # Reset the edited image if exists
        self.edited_new_image = None

        self.create_gan_inversion_button.grid_remove()
        self.edited_image_label.grid_remove()
        self.original_image_label.grid_remove()


        if self.image_on_window:
            self.original_img.grid_remove()
            self.image_on_window = False
        if self.inversion_image_on_window:
            self.new_img_label.grid_remove()
            self.inversion_image_on_window = False

        self.inverted_image_path = filedialog.askopenfilename()

        if self.inverted_image_path:

            self.user_root_folder = os.path.dirname(os.path.dirname(self.inverted_image_path))
            
            self.original_image_path = self.get_file_path(folder_path=os.path.join(self.user_root_folder, "input_image"), file_extention=".jpeg")
            if self.original_image_path is None:
                print(f"No Input Image in the chosen dir with the extention .jpeg")
                return
            
            self.w_path = self.get_file_path(folder_path=os.path.join(self.user_root_folder, "embeddings"), file_extention=".pt")
            if self.original_image_path is None:
                print(f"No Input Vector in the embeddings dir with the extention .pt")
                return
            
            self.new_generator_path = self.get_file_path(folder_path=os.path.join(self.user_root_folder, "generator"), file_extention=".pt")
            if self.original_image_path is None:
                print(f"No Input Vector in the generator dir with the extention .pt")
                return

            original_img = Image.open(self.original_image_path)
            original_img.thumbnail((250, 250))
            original_img = ImageTk.PhotoImage(original_img)
            self.original_img = ttk.Label(self, image=original_img)
            self.original_img.image = original_img
            self.original_img.grid(row=4, column=2, columnspan=2, padx=30, pady=10)
            self.original_image_label.grid(row=3, column=2, columnspan=2, padx=30, pady=10)
            self.image_on_window = True

            new_image = Image.open(self.inverted_image_path)
            # Display the new image
            new_image.thumbnail((250, 250))
            new_image = ImageTk.PhotoImage(new_image)
            self.new_img_label = ttk.Label(self, image=new_image)
            self.new_img_label.image = new_image
            self.new_img_label.grid(row=4, column=5, columnspan=2, padx=30, pady=10)
            self.edited_image_label.grid(row=3, column=5, columnspan=2, padx=30, pady=10)
            self.inversion_image_on_window = True

            self.generate_button.grid(row=12, column=4, padx=30, pady=10, sticky="ew")
  
    def create_gan_inversion(self):
        # Step 1: Get the folder path and image name
        folder_path, image_file = os.path.split(self.image_path)
        image_name, _ = os.path.splitext(image_file)

        # Step 2: Create a new folder named after the image name
        self.user_root_folder = os.path.join(folder_path, f"play_with_{image_name}")
        if not os.path.exists(self.user_root_folder):
            os.mkdir(self.user_root_folder)

        # Step 3: Create the four specified subfolders
        subfolders = ["input_image", "inversion_image", "output_images", "embeddings", "generator"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(self.user_root_folder, subfolder)
            if not os.path.exists(subfolder_path):
                os.mkdir(subfolder_path)

        # Step 4: Copy the image to the "input_image" folder
        destination_path = os.path.join(self.user_root_folder, "input_image", f"{image_name}.jpeg")
        shutil.move(self.processed_image_path, destination_path)

        paths_config.processed_images_dir = os.path.join(self.user_root_folder, "input_image")

        # paths to the embeding vector folder and file
        paths_config.embedding_base_dir = os.path.join(self.user_root_folder, "embeddings")
        self.w_path = os.path.join(paths_config.embedding_base_dir, f"{image_name}.pt")
        print(f"_____ W path saved by test_GUI: {self.w_path} _____")

        # path to the generator model folder and file
        paths_config.generaator_dir = os.path.join(self.user_root_folder, "generator")
        self.new_generator_path = os.path.join(paths_config.generaator_dir, f"{image_name}_model.pt")
        print(f"_____ Generator path saved by test_GUI: {self.new_generator_path} _____")

        model_id = pti_inversion.run_PTI()
        with open(self.new_generator_path, 'rb') as f_new: 
            new_G = torch.load(f_new).cuda()

        w_pivot = torch.load(self.w_path)

        new_image = new_G.synthesis(w_pivot, noise_mode='const', force_fp32 = True)

        new_image = (new_image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).detach().cpu().numpy()[0] 
        new_image = Image.fromarray(new_image,mode='RGB')
        new_image.save(os.path.join(self.user_root_folder, "inversion_image", f"{image_name}.jpeg"))
        self.progress.stop()
        self.progress.grid_remove()
        self.waiting_massage.grid_remove()

        # Display the new image
        new_image.thumbnail((250, 250))
        new_image = ImageTk.PhotoImage(new_image)
        self.new_img_label = ttk.Label(self, image=new_image)
        self.new_img_label.image = new_image
        self.new_img_label.grid(row=4, column=5, columnspan=2, padx=30, pady=10)
        self.edited_image_label.grid(row=3, column=5, columnspan=2, padx=30, pady=10)
        self.inversion_image_on_window = True

        self.generate_button.grid(row=12, column=4, padx=30, pady=10, sticky="ew")

    def start_gan_inversion(self):

        self.progress.grid(row=6, column=4, padx=10, pady=10, sticky="ew")
        self.progress.start(10)
        self.waiting_massage.grid(row=5, column=4, padx=10, pady=10, sticky="ew")
        threading.Thread(target=self.create_gan_inversion).start()
 
    def load_direction_tensors(self, directory):
        direction_tensors = {}
        for file in os.listdir(directory):
            if file.endswith(".pt"):
                name = file[:-3]  # Remove the .pt extension
                path = os.path.join(directory, file)
                direction_tensors[name] = path
        return direction_tensors

    def add_direction_widget(self):
        widget = DirectionWidget(self, self.direction_tensors, self.update_latent_direction)
        # Use grid and place each new widget in the next available row
        widget.grid(row=self.next_grid_row, column=4, sticky="nsew", padx=5, pady=5)
        self.direction_widgets.append(widget)
        # Increment the row counter so the next widget will be below
        self.next_grid_row += 1

    def update_latent_direction(self, direction_name, value):
        print(f"Updating {direction_name} with value {value}")
        # Here you would adjust the `edited_latent` variable
        # This is just a placeholder for demonstration

    def get_edited_w(self, start_w):
        edited_latent = start_w.clone()
        for widget in self.direction_widgets:
            direction_name = widget.variable.get()
            if direction_name in self.direction_tensors:
                direction_tensor = torch.load(self.direction_tensors[direction_name]).cuda()
                factor = widget.scale.get() if widget.scale else 0
                edited_latent += factor * direction_tensor
        return edited_latent

    def generate_new_image(self):

        w_pivot = torch.load(self.w_path)
        with open(self.new_generator_path, 'rb') as f_new: 
            new_G = torch.load(f_new).cuda()
        
        new_latent = self.get_edited_w(w_pivot)

        self.edited_new_image = new_G.synthesis(new_latent, noise_mode='const', force_fp32 = True)
        
        # Display the new image
        self.edited_new_image = (self.edited_new_image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).detach().cpu().numpy()[0] 
        self.edited_new_image = Image.fromarray(self.edited_new_image, mode='RGB')
        displayed_new_image = self.edited_new_image
        displayed_new_image.thumbnail((250, 250))
        displayed_new_image = ImageTk.PhotoImage(displayed_new_image)
        self.new_img_label = ttk.Label(self, image=displayed_new_image)
        self.new_img_label.image = displayed_new_image
        self.new_img_label.grid(row=4, column=5, columnspan=2, padx=30, pady=10)

        self.save_button.grid(row=5, column=5, columnspan=2, padx=30, pady=10)
