import pickle
import torch
from tqdm import tqdm
from torchvision.transforms import transforms
from torch.utils.data import DataLoader

from configs import paths_config, hyperparameters, global_config
from training.projectors import w_projector
from utils.ImagesDataset import ImagesDataset
from utils.align_data import pre_process_images


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


old_G = load_G()

# images_dir = '/home/yoavaviv/GAN-pain/shoulder_pain_dataset/test_images'
# embedding_dir = '/home/yoavaviv/GAN-pain/shoulder_pain_dataset/emmbbeded_images'

# Align and crop raw images and save them inside '/home/yoavaviv/GAN-pain/processed_images'
pre_process_images(paths_config.input_images_dir)
print(f"Images aligned and saved in GAN-pain/processed_images dir")

dataloader = create_dataloader(images_dir=paths_config.processed_images_dir)

for fname, image in tqdm(dataloader):
    image_name = fname[0]

    # w_pivot = base.calc_inversions(image, image_name)
    # torch.save(w_pivot, f'{embedding_dir}/{image_name}.pt')
    embbeded_image = get_embbeded_image(image, image_name, old_G)
    
    embbeded_image = embbeded_image.to(global_config.device)

    torch.save(embbeded_image, f'{paths_config.embedding_base_dir}/{image_name}.pt')
