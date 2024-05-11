import numpy as np
from api.configs import paths_config
import torch
from sklearn import svm
from api.explore.train_boundary import train_boundary

latent_codes = np.load('/home/yoavaviv/GAN-pain/shoulder_pain_dataset/latent_codes.npy')

print(f" latent_codes shape = {latent_codes.shape}")

print(f" length of latent_codes shape = {len(latent_codes.shape)}")

pain_scores = np.load('/home/yoavaviv/GAN-pain/shoulder_pain_dataset/pain_scores.npy')

print(f" pain_scores shape = {pain_scores.shape}")

# num_samples = latent_codes.shape[0]

# clf = svm.SVC(kernel='linear')
# classifier = clf.fit(latent_codes, pain_scores)

# val_prediction = classifier.predict(latent_codes)
# correct_num = np.sum(pain_scores == val_prediction)
# print(f'Accuracy for validation set: '
#             f'{correct_num} / {num_samples} = '
#             f'{correct_num / (num_samples):.6f}')

boundary = train_boundary(latent_codes=latent_codes, scores=pain_scores,split_ratio=0.95)

boundary_tensor = torch.from_numpy(boundary)

torch.save(boundary_tensor, './database/editing_directions/interfacegan_directions/pain.pt')

print(f"boundary.shape: {boundary.shape}")

# print(f"boundary: {boundary}")

# interfacegan_directions = {'age': f'{paths_config.interfacegan_age}',
#                                 'smile': f'{paths_config.interfacegan_smile}',
#                                 'rotation': f'{paths_config.interfacegan_rotation}'}
# interfacegan_directions_tensors = {name: torch.load(path).cuda() for name, path in
#                                         interfacegan_directions.items()}

# for direction in ['rotation', 'smile', 'age']:

#     print(f"interfacegan_directions_tensors[{direction}]: {interfacegan_directions_tensors[direction].shape}")