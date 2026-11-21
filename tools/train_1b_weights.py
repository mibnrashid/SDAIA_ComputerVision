"""train_1b_weights.py — train the three Lab 1B models and save their weights
for the notebook's escape cells (notebooks/weights/*.pt).

    python tools/train_1b_weights.py            # GPU: ~10 min · CPU: ~30–60 min

Uses exactly the architectures and settings of Lab 1B: MLP 5 epochs,
SmallCNN 8 epochs, SmallCNN + augmentation + dropout 12 epochs, Adam 1e-3.
"""
import os
import time

import torch
import torch.nn as nn
import torchvision
from torch.utils.data import DataLoader
from torchvision import transforms

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'notebooks', 'weights')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MEAN, STD = (0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)


class SmallCNN(nn.Module):
    def __init__(self, dropout=0.0):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.head = nn.Sequential(
            nn.Flatten(), nn.Linear(128 * 4 * 4, 256), nn.ReLU(), nn.Dropout(dropout), nn.Linear(256, 10),
        )

    def forward(self, x):
        return self.head(self.features(x))


def mlp():
    return nn.Sequential(nn.Flatten(), nn.Linear(3072, 512), nn.ReLU(), nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, 10))


def run(model, loader, test_loader, epochs, name):
    model.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    for ep in range(epochs):
        t0 = time.time(); model.train()
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            loss = loss_fn(model(x), y)
            opt.zero_grad(); loss.backward(); opt.step()
        model.eval(); c = t = 0
        with torch.no_grad():
            for x, y in test_loader:
                c += (model(x.to(DEVICE)).argmax(1).cpu() == y).sum().item(); t += len(y)
        print(f'{name} epoch {ep + 1}/{epochs} test acc {c / t:.3f} ({time.time() - t0:.0f}s)', flush=True)
    os.makedirs(OUT, exist_ok=True)
    model.cpu()
    torch.save(model.state_dict(), os.path.join(OUT, name))
    print('saved', name, f'final test acc {c / t:.3f}')
    return c / t


def main():
    torch.manual_seed(0)
    norm = transforms.Normalize(MEAN, STD)
    plain = transforms.Compose([transforms.ToTensor(), norm])
    aug = transforms.Compose([transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip(), transforms.ToTensor(), norm])
    data = os.path.join(ROOT, '.cache-cifar')
    tr = torchvision.datasets.CIFAR10(data, train=True, download=True, transform=plain)
    tr_aug = torchvision.datasets.CIFAR10(data, train=True, download=True, transform=aug)
    te = torchvision.datasets.CIFAR10(data, train=False, download=True, transform=plain)
    workers = 2 if DEVICE == 'cuda' else 0
    L = DataLoader(tr, batch_size=128, shuffle=True, num_workers=workers)
    LA = DataLoader(tr_aug, batch_size=128, shuffle=True, num_workers=workers)
    T = DataLoader(te, batch_size=256, num_workers=workers)
    run(mlp(), L, T, 5, 'mlp_cifar10.pt')
    run(SmallCNN(), L, T, 8, 'cnn_cifar10.pt')
    run(SmallCNN(dropout=0.5), LA, T, 12, 'cnn_aug_cifar10.pt')


if __name__ == '__main__':
    main()
