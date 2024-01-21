# Python packages imports
import tkinter as tk
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


class PlayPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
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

        self.generate_button = ttk.Button(self, text="Generate New Image", command=self.on_generate_new_image)
        self.smile_scale = ttk.Scale(self, from_=-3, to=3, orient='horizontal', command=self.update_smile_label)
        self.age_scale = ttk.Scale(self, from_=-3, to=3, orient='horizontal', command=self.update_age_label)
        self.pose_scale = ttk.Scale(self, from_=-3, to=3, orient='horizontal', command=self.update_pose_label)

        self.smile_label = ttk.Label(self, text="Smile: 0")
        self.age_label = ttk.Label(self, text="Age: 0")
        self.pose_label = ttk.Label(self, text="Pose: 0")

        self.save_button = ttk.Button(self, text="Save image", command=self.save_image)
        

    def upload_image(self):

        # Reset the edited image if exists
        self.edited_new_image = None

        self.create_gan_inversion_button.grid_remove()
        self.edited_image_label.grid_remove()
        self.original_image_label.grid_remove()
        self.generate_button.grid_remove()
        self.smile_scale.grid_remove()
        self.age_scale.grid_remove()
        self.pose_scale.grid_remove()
        self.smile_label.grid_remove()
        self.age_label.grid_remove()
        self.pose_label.grid_remove()


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

            self.add_scrollbars()
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

        # Code to add scrollbars and button after GAN inversion
        self.add_scrollbars()
        self.generate_button.grid(row=12, column=4, padx=30, pady=10, sticky="ew")

    def start_gan_inversion(self):

        self.progress.grid(row=6, column=4, padx=10, pady=10, sticky="ew")
        self.progress.start(10)
        self.waiting_massage.grid(row=5, column=4, padx=10, pady=10, sticky="ew")
        threading.Thread(target=self.create_gan_inversion).start()
    
    def add_scale_range_labels(self, row, column):
        label_min = ttk.Label(self, text="-3")
        label_min.grid(row=row, column=column, padx=(0, 0), pady=(0, 5), sticky="w")
        
        label_max = ttk.Label(self, text="3")
        label_max.grid(row=row, column=column, padx=(0, 0), pady=(0, 5), sticky="e")

    def update_smile_label(self, value):
        self.smile_label.config(text=f"Smile: {float(value):.1f}")

    def update_age_label(self, value):
        self.age_label.config(text=f"Age: {float(value):.1f}")

    def update_pose_label(self, value):
        self.pose_label.config(text=f"Pose: {float(value):.1f}")
    
    def add_scrollbars(self):

        # Label and Scale for Smile
        self.smile_scale.set(0)  # Set initial value to 0
        self.smile_scale.grid(row=7, column=4, padx=30, pady=10, sticky="ew")
        self.smile_label.grid(row=6, column=4, padx=30, pady=(10, 0), sticky="s")
        self.add_scale_range_labels(7, 4)

        # Label and Scale for Age
        self.age_scale.set(0)  # Set initial value to 0
        self.age_scale.grid(row=9, column=4, padx=30, pady=10, sticky="ew")
        self.age_label.grid(row=8, column=4, padx=30, pady=(10, 0), sticky="s")
        self.add_scale_range_labels(9, 4)

        # Label and Scale for Pose
        self.pose_scale.set(0)  # Set initial value to 0
        self.pose_scale.grid(row=11, column=4, padx=30, pady=10, sticky="ew")
        self.pose_label.grid(row=10, column=4, padx=30, pady=(10, 0), sticky="s")
        self.add_scale_range_labels(11, 4)

    def on_generate_new_image(self):

        self.smile = self.smile_scale.get()
        self.age = self.age_scale.get()
        self.pose = self.pose_scale.get()

        self.factors = [self.pose, self.smile, self.age]

        # Call the method to generate new image
        self.generate_new_image(self.factors)

    def get_edited_w(self, start_w, factors):

        edited_latent = start_w

        # self.latent_editor = LatentEditor()
        
        self.interfacegan_directions = {'age': f'{paths_config.interfacegan_age}',
                                        'smile': f'{paths_config.interfacegan_smile}',
                                        'rotation': f'{paths_config.interfacegan_rotation}'}
        self.interfacegan_directions_tensors = {name: torch.load(path).cuda() for name, path in
                                                self.interfacegan_directions.items()}
        
        for factor, direction in zip(factors, ['rotation', 'smile', 'age']):

            edited_latent = edited_latent + factor * self.interfacegan_directions_tensors[direction]

        return edited_latent
    
    def generate_new_image(self, factors):

        w_pivot = torch.load(self.w_path)
        with open(self.new_generator_path, 'rb') as f_new: 
            new_G = torch.load(f_new).cuda()
        
        new_latent = self.get_edited_w(w_pivot, factors)

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
