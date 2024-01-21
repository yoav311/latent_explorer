## Pretrained models paths
# e4e = '/home/yoavaviv/GAN-pain/pretrained_models/e4e_ffhq_encode.pt'
# stylegan2_ada_ffhq = '/home/yoavaviv/GAN-pain/pretrained_models/ffhq.pkl'
# style_clip_pretrained_mappers = ''
# ir_se50 = './pretrained_models/model_ir_se50.pth'
# dlib = '/home/yoavaviv/GAN-pain/pretrained_models/align.dat'

e4e = './database/pretrained_models/e4e_ffhq_encode.pt'
stylegan2_ada_ffhq = './database/pretrained_models/ffhq.pkl'
style_clip_pretrained_mappers = ''
ir_se50 = './database/pretrained_models/model_ir_se50.pth'
dlib = './database/pretrained_models/align.dat'

## Dirs for output files
checkpoints_dir = './checkpoints'
embedding_base_dir = './embeddings'
styleclip_output_dir = './StyleCLIP_results'
experiments_output_dir = './output'

## Input info
### Input dir, where the images reside
input_images_dir = '/home/yoavaviv/GAN-pain/input_images'
processed_images_dir = '/home/yoavaviv/GAN-pain/processed_images'
### Inversion identifier, used to keeping track of the inversion results. Both the latent code and the generator
input_data_id = 'embedded_image'

generaator_dir = ''

## Keywords
pti_results_keyword = 'PTI'
e4e_results_keyword = 'e4e'
sg2_results_keyword = 'SG2'
sg2_plus_results_keyword = 'SG2_plus'
multi_id_model_type = 'multi_id'

## Edit directions
interfacegan_age = './database/editing_directions/interfacegan_directions/age.pt'
interfacegan_smile = './database/editing_directions/interfacegan_directions/smile.pt'
interfacegan_rotation = './database/editing_directions/interfacegan_directions/rotation.pt'
ffhq_pca = 'editings/ganspace_pca/ffhq_pca.pt'
