import dlib
import glob
import os, sys, inspect
from tqdm import tqdm

from api.image_processing.face_alignment import align_face
from api.configs import paths_config

def pre_process_images(raw_images_path, processed_images_dir=None):
    current_directory = os.getcwd()
    print(f"current_directory:{current_directory}")
    print(f" processed_images_dir: {processed_images_dir}")

    IMAGE_SIZE = 1024
    predictor = dlib.shape_predictor(paths_config.dlib)

    os.chdir(raw_images_path)
    processed_images_dir = paths_config.processed_images_dir if processed_images_dir is None else processed_images_dir
    # images_names = glob.glob(f'*')
    images_names = glob.glob('*.jpg') + glob.glob('*.jpeg') + glob.glob('*.png') + glob.glob('*.PNG')

    print(f"images_names: {images_names}")


    aligned_images = []
    for image_name in tqdm(images_names):
        try:
            aligned_image = align_face(filepath=f'{raw_images_path}/{image_name}',
                                       predictor=predictor, output_size=IMAGE_SIZE)
            aligned_images.append(aligned_image)
        except Exception as e:
            print(e)
    
    if processed_images_dir is None:
        os.chdir(raw_images_path)

    # os.makedirs(processed_images_dir, exist_ok=True)
    for image, name in zip(aligned_images, images_names):
        real_name = name.split('.')[0]
        saving_path = f'{processed_images_dir}/{real_name}.jpeg'
        print(f"saving_path: {saving_path}")
        image.save(saving_path)

    os.chdir(current_directory)


if __name__ == "__main__":
    pre_process_images('')
