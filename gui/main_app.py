import tkinter as tk
import tkinter.font as tkFont
import os
import shutil
import dlib
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import torch
import threading

from api.explore.calc_inversion import calc_inversiones
from api.image_processing.face_alignment import align_face
from api.configs import paths_config
from api.play import run_pti as pti_inversion


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
        

    def upload_image(self):

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

            self.chosen_image_dir = os.path.dirname(os.path.dirname(self.inverted_image_path))
            
            self.original_image_path = self.get_file_path(folder_path=os.path.join(self.chosen_image_dir, "input_image"), file_extention=".png")
            if self.original_image_path is None:
                print(f"No Input Image in the chosen dir with the extention .jpeg")
                return
            
            self.w_path = self.get_file_path(folder_path=os.path.join(self.chosen_image_dir, "embeddings"), file_extention=".pt")
            if self.original_image_path is None:
                print(f"No Input Vector in the embeddings dir with the extention .pt")
                return
            
            self.new_generator_path = self.get_file_path(folder_path=os.path.join(self.chosen_image_dir, "generator"), file_extention=".pt")
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
        new_folder_path = os.path.join(folder_path, f"play_with_{image_name}")
        if not os.path.exists(new_folder_path):
            os.mkdir(new_folder_path)

        # Step 3: Create the four specified subfolders
        subfolders = ["input_image", "inversion_image", "output_images", "embeddings", "generator"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(new_folder_path, subfolder)
            if not os.path.exists(subfolder_path):
                os.mkdir(subfolder_path)

        # Step 4: Copy the image to the "input_image" folder
        destination_path = os.path.join(new_folder_path, "input_image", image_file)
        shutil.move(self.processed_image_path, destination_path)

        paths_config.processed_images_dir = os.path.join(new_folder_path, "input_image")

        # paths to the embeding vector folder and file
        paths_config.embedding_base_dir = os.path.join(new_folder_path, "embeddings")
        self.w_path = os.path.join(paths_config.embedding_base_dir, f"{image_name}.pt")
        print(f"_____ W path saved by test_GUI: {self.w_path} _____")

        # path to the generator model folder and file
        paths_config.generaator_dir = os.path.join(new_folder_path, "generator")
        self.new_generator_path = os.path.join(paths_config.generaator_dir, f"{image_name}_model.pt")
        print(f"_____ Generator path saved by test_GUI: {self.new_generator_path} _____")

        model_id = pti_inversion.run_PTI()
        with open(self.new_generator_path, 'rb') as f_new: 
            new_G = torch.load(f_new).cuda()

        w_pivot = torch.load(self.w_path)

        new_image = new_G.synthesis(w_pivot, noise_mode='const', force_fp32 = True)

        new_image = (new_image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).detach().cpu().numpy()[0] 
        new_image = Image.fromarray(new_image,mode='RGB')
        new_image.save(os.path.join(new_folder_path, "inversion_image", f"{image_name}.jpeg"))
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

        edited_new_image = new_G.synthesis(new_latent, noise_mode='const', force_fp32 = True)
        
        # Display the new image
        edited_new_image = (edited_new_image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).detach().cpu().numpy()[0] 
        edited_new_image = Image.fromarray(edited_new_image, mode='RGB')
        edited_new_image.thumbnail((250, 250))
        edited_new_image = ImageTk.PhotoImage(edited_new_image)
        self.new_img_label = ttk.Label(self, image=edited_new_image)
        self.new_img_label.image = edited_new_image
        self.new_img_label.grid(row=4, column=5, columnspan=2, padx=30, pady=10)

class ExplorePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.dataset_dir = None  # Variable to store the selected directory path

        ttk.Button(self, text="Choose Dataset Dir", command=self.choose_dataset_dir).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(self, text="Calculate Embeddings", command=self.calc_inversions).grid(row=0, column=1, padx=10, pady=10)
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

class GetStartedPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        ttk.Button(self, text="Go Home", command=lambda: controller.show_frame(HomePage)).grid(row=0, column=0, padx=10, pady=10)

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
        # Make the nav_bar expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)  # New column for sidebar
        self.grid_columnconfigure(2, weight=1)  # Main content column

        
        # Adjusting the expansion of the navigation bar
        # for i in range(4):
        #     nav_bar.grid_rowconfigure(i, weight=0)
        # nav_bar.grid_rowconfigure(4, weight=1)

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