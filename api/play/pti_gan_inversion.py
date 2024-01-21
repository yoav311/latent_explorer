import numpy as np
from PIL import Image
import torch
from IPython.display import display
import matplotlib.pyplot as plt

from api.configs import paths_config
from api.image_processing.align_data import pre_process_images
from api.play import run_pti as pti_inversion

def display_alongside_source_image(images): 
    res = np.concatenate([np.array(image) for image in images], axis=1) 
    return Image.fromarray(res) 

def load_generator(model_id, image_name):   
  with open(f'{paths_config.checkpoints_dir}/model_{model_id}_{image_name}.pt', 'rb') as f_new: 
    new_G = torch.load(f_new).cuda()

  return new_G


def save_syn_images(syn_images): 
  for idx, img in enumerate(syn_images): 
      img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).detach().cpu().numpy()[0] 
      plt.axis('off') 
      resized_image = Image.fromarray(img,mode='RGB').resize((256,256))
      resized_image.save(f'./outputs/{idx}.jpeg') 


# The path is '/home/yoavaviv/GAN-pain/input_images'
raw_images_dir_path = paths_config.input_images_dir
# Align and crop raw images and save them inside '/home/yoavaviv/GAN-pain/processed_images'
pre_process_images(raw_images_dir_path)
print(f"Images aligned and saved in GAN-pain/processed_images dir")

# Run PTI gan inversion. Save the tuned generator in checkpoints/model_{model_id}_{image_name}.pt'. Save embbeding vectors in embbedings/embedded_images/PTI
model_id = pti_inversion.run_PTI()
image_name = 'jenifer'
use_multi_id_training = False

generator_type = paths_config.multi_id_model_type if use_multi_id_training else image_name
pti_G = load_generator(model_id, generator_type)

w_path_dir = f'{paths_config.embedding_base_dir}/{paths_config.input_data_id}'
embedding_dir = f'{w_path_dir}/{paths_config.pti_results_keyword}/{image_name}'
w_pivot = torch.load(f'{embedding_dir}/0.pt')

new_image = pti_G.synthesis(w_pivot, noise_mode='const', force_fp32 = True)

save_syn_images([new_image])