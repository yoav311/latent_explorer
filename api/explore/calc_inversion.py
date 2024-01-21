import pickle
import torch
from tqdm import tqdm
from torchvision.transforms import transforms
from torch.utils.data import DataLoader

from api.configs import paths_config, hyperparameters, global_config
from api.inversion_training.projectors import w_projector
from api.image_processing.ImagesDataset import ImagesDataset
from api.image_processing.align_data import pre_process_images

def create_dataloader(images_dir):
    dataset = ImagesDataset(images_dir, transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])]))

    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    return dataloader

def load_G():
    with open(paths_config.stylegan2_ada_ffhq, 'rb') as f:
        old_G = pickle.load(f)['G_ema'].to(global_config.device).eval()
        old_G = old_G.float()

    return old_G

def get_embbeded_image(image, image_name, old_G, use_wandb=False):
    id_image = torch.squeeze((image.to(global_config.device) + 1) / 2) * 255
    w = w_projector.project(old_G, id_image, device=torch.device(global_config.device), w_avg_samples=600,
                            num_steps=hyperparameters.first_inv_steps, w_name=image_name,
                            use_wandb=use_wandb)
    return w


def calc_inversiones(input_images_dir=None, processed_images_dir=None, embbeding_images_dir = None):

    input_images_dir = paths_config.input_images_dir if input_images_dir is None else input_images_dir
    processed_images_dir = paths_config.processed_images_dir if processed_images_dir is None else processed_images_dir
    embbeding_images_dir = paths_config.embedding_base_dir if embbeding_images_dir is None else embbeding_images_dir

    # Align and crop raw images and save them inside '/home/yoavaviv/GAN-pain/processed_images'
    pre_process_images(input_images_dir, processed_images_dir=processed_images_dir)

    dataloader = create_dataloader(images_dir=processed_images_dir)

    old_G = load_G()

    for fname, image in tqdm(dataloader):
        image_name = fname[0]

        # w_pivot = base.calc_inversions(image, image_name)
        # torch.save(w_pivot, f'{embedding_dir}/{image_name}.pt')
        embbeded_image = get_embbeded_image(image, image_name, old_G)
        
        embbeded_image = embbeded_image.to(global_config.device)

        torch.save(embbeded_image, f'{embbeding_images_dir}/{image_name}.pt')

if __name__ == "__main__":
    calc_inversiones()

    # input_images_dir='/home/yoavaviv/test GUI/input_images',
    # processed_images_dir='/home/yoavaviv/test GUI/processed_images',
    # embbeding_images_dir = '/home/yoavaviv/test GUI/embeddings'
