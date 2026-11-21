from .common import md, code, check, how_to_use, gpu_check, RAW

META = dict(id='1B', file='Lab_1B', title='Your first CNN', day=1, block='Day 1 · B5 (finish tonight)',
            goal='Train an MLP baseline and a small CNN on CIFAR-10, trace shapes layer by layer, add augmentation and dropout, read the curves and the confusion matrix, then compare with a pretrained ResNet-18.',
            libs='PyTorch, torchvision, scikit-learn, Matplotlib', gpu=True)

ESCAPE = '''# Escape hatch: load our trained weights instead of training
# Use this if the training cell above was too slow or crashed. It downloads weights we trained with exactly this code.
USE_PRETRAINED = False   # ← set to True and run this cell
if USE_PRETRAINED:
    url = "{raw}/notebooks/weights/{fname}"
    {model}.load_state_dict(torch.hub.load_state_dict_from_url(url, map_location=DEVICE, file_name="{fname}"))
    {model}.to(DEVICE)
    print("Loaded {fname}. Test accuracy:", round(evaluate({model}, test_loader)[1], 3))'''

CELLS = [
    how_to_use('1B', META['title'], META['goal'], 'Day 1 · Block 5 · Acts 4–7', 30),
    gpu_check('a 10,000-image subset and fewer epochs'),
    code('''import time, numpy as np, matplotlib.pyplot as plt
import torch.nn as nn
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader, Subset
torch.manual_seed(0); np.random.seed(0)
print("torch", torch.__version__, "| torchvision", torchvision.__version__)''',
         'Imports and seeds', 'torch and torchvision versions', '—'),

    md('''## 4 · Learning from data

### 4.1 · The data: CIFAR-10
50,000 training and 10,000 test images, 32 × 32 colour, 10 classes. `ToTensor()` changes the layout from (H, W, C) to **(C, H, W)** *and* divides by 255; `Normalize` then centres each channel.'''),
    code('''MEAN, STD = (0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)
normalize = transforms.Normalize(MEAN, STD)
plain_tf = transforms.Compose([transforms.ToTensor(), normalize])

train_full = torchvision.datasets.CIFAR10("data", train=True, download=True, transform=plain_tf)
test_full = torchvision.datasets.CIFAR10("data", train=False, download=True, transform=plain_tf)
CLASSES = train_full.classes
n_train, n_test = (10000, 2000) if FAST else (len(train_full), len(test_full))
train_set = Subset(train_full, range(n_train))
test_set = Subset(test_full, range(n_test))
train_loader = DataLoader(train_set, batch_size=128, shuffle=True, num_workers=2)
test_loader = DataLoader(test_set, batch_size=256, num_workers=2)
x, y = next(iter(train_loader))
print("batch:", tuple(x.shape), "labels:", tuple(y.shape), "| train", n_train, "test", n_test)
print("iterations per epoch:", len(train_loader))''',
         'Downloads CIFAR-10 (170 MB) and builds the DataLoaders',
         'batch: (128, 3, 32, 32) labels: (128,) | train 50000 test 10000 | iterations per epoch: 391',
         'Slow download on venue Wi-Fi → wait ~1 min; "num_workers" warning on CPU is harmless', run=True),
    code('''imgs = x[:16] * torch.tensor(STD).view(3, 1, 1) + torch.tensor(MEAN).view(3, 1, 1)
fig, axes = plt.subplots(2, 8, figsize=(12, 3.4))
for ax, im, lab in zip(axes.ravel(), imgs, y[:16]):
    ax.imshow(im.permute(1, 2, 0).clamp(0, 1)); ax.set_title(CLASSES[lab], fontsize=9); ax.axis("off")
plt.show()''',
         'Shows 16 training images with labels', 'A 2 × 8 grid of tiny, blurry images (plane, car, bird, cat …)',
         'Forgetting to un-normalise or to permute (C,H,W)→(H,W,C) gives a crash or odd colours'),

    md('''### 4.2 · Training and evaluation helpers
This is the five-line training loop from slide 1.90. Read it line by line.'''),
    code('''loss_fn = nn.CrossEntropyLoss()

def train_one_epoch(model, loader, optimizer):
    model.train()                                   # dropout on, BatchNorm uses the batch
    total, correct, loss_sum = 0, 0, 0.0
    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        outputs = model(images)                     # forward
        loss = loss_fn(outputs, labels)             # how wrong
        @@ optimizer.zero_grad(); loss.backward(); optimizer.step() ||| pass  # TODO: clear old gradients, compute gradients, update weights (three calls on one line, separated by ;)
        loss_sum += loss.item() * len(labels)
        correct += (outputs.argmax(1) == labels).sum().item(); total += len(labels)
    return loss_sum / total, correct / total

@torch.no_grad()
def evaluate(model, loader):
    model.eval()                                    # dropout off, BatchNorm uses saved statistics
    total, correct, loss_sum = 0, 0, 0.0
    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        outputs = model(images)
        loss_sum += loss_fn(outputs, labels).item() * len(labels)
        correct += (outputs.argmax(1) == labels).sum().item(); total += len(labels)
    return loss_sum / total, correct / total

def fit(model, epochs, lr=1e-3, loader=None):
    loader = loader or train_loader
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    hist = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for ep in range(epochs):
        t0 = time.time()
        tl, ta = train_one_epoch(model, loader, opt)
        vl, va = evaluate(model, test_loader)
        for k, v in zip(hist, (tl, vl, ta, va)): hist[k].append(v)
        print(f"epoch {ep+1}/{epochs}  train loss {tl:.3f} acc {ta:.3f} | val loss {vl:.3f} acc {va:.3f} | {time.time()-t0:.0f}s")
    return hist''',
         'TODO 1: the three optimizer lines of the training loop; evaluate() and fit() helpers', 'No output (functions defined)',
         'Forgetting zero_grad piles gradients up across batches: loss jumps around'),
    check('not torch.equal(_before, _m[1].weight.detach())', 'One training step changed the weights: your loop updates the model.',
          'optimizer.zero_grad(); loss.backward(); optimizer.step()',
          setup='''from torch.utils.data import TensorDataset
_m = nn.Sequential(nn.Flatten(), nn.Linear(4, 2)).to(DEVICE)
_before = _m[1].weight.detach().clone()
_dl = DataLoader(TensorDataset(torch.randn(8, 1, 2, 2), torch.randint(0, 2, (8,))), batch_size=8)
train_one_epoch(_m, _dl, torch.optim.SGD(_m.parameters(), lr=0.5))'''),
    md('''### 4.3 · The obvious attempt: an MLP
Flatten the 3 × 32 × 32 image into 3,072 numbers and use fully connected layers (3,072 → 512 → 256 → 10).'''),
    code('''mlp = nn.Sequential(
    nn.Flatten(),
    nn.Linear(3 * 32 * 32, 512), nn.ReLU(),
    nn.Linear(512, 256), nn.ReLU(),
    nn.Linear(256, 10),
).to(DEVICE)
@@ n_params = sum(p.numel() for p in mlp.parameters()) ||| n_params = 0  # TODO: count the parameters: sum of p.numel() over mlp.parameters()
print(f"MLP parameters: {n_params:,}")''',
         'TODO 2: build the MLP and count its parameters', 'MLP parameters: 1,707,274', 'Counting only weights (no biases) gives 1,703,936'),
    check('n_params == 1_707_274', 'MLP has 1,707,274 parameters (≈ 1.7 M, slide 1.82).',
          'sum(p.numel() for p in mlp.parameters())'),
    code('''mlp_hist = fit(mlp, epochs=2 if FAST else 5)''',
         'Trains the MLP (about 1 min on a T4)', 'Five epoch lines; val accuracy ends around 0.48–0.53',
         'Loss stays at 2.30 → TODO 1 is wrong (nothing is being updated)', run=True),
    code(ESCAPE.format(raw=RAW, fname='mlp_cifar10.pt', model='mlp'),
         'Escape: load our trained MLP weights instead', 'Nothing unless USE_PRETRAINED = True; then "Loaded … Test accuracy: ~0.52"',
         'Before the repo is public the download fails → train instead'),

    md('''## 5 · The convolutional neural network

The model from slide 1.81: three conv blocks (conv 3×3, padding 1, ReLU, max-pool 2) then a small classifier head.'''),
    code('''class SmallCNN(nn.Module):
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

cnn = SmallCNN().to(DEVICE)
print(f"CNN parameters: {sum(p.numel() for p in cnn.parameters()):,}")''',
         'Defines the small CNN', 'CNN parameters: 620,362', 'Wrong in_features in the first Linear (e.g. 128*8*8) → shape error at the first batch'),
    md('''### 5.1 · Trace the shapes, layer by layer
Use the output-size formula ⌊(W − K + 2P)/S⌋ + 1. Predict each line before you run it.'''),
    code('''x = torch.zeros(1, 3, 32, 32, device=DEVICE)
print(f"{'input':<28}{tuple(x.shape)}")
for layer in list(cnn.features) + list(cnn.head):
    @@ x = layer(x) ||| pass  # TODO: pass x through this layer (x = layer(x))
    print(f"{layer.__class__.__name__:<28}{tuple(x.shape)}")
final_shape = tuple(x.shape)''',
         'TODO 3: push a dummy image through each layer and print shapes',
         'Conv2d (1, 32, 32, 32) → MaxPool2d (1, 32, 16, 16) → … → Flatten (1, 2048) → Linear (1, 10)', 'Printing before applying the layer shifts every line by one'),
    check('final_shape == (1, 10)', 'Final output is (1, 10): ten class scores.', 'inside the loop write x = layer(x)'),
    code('''cnn_hist = fit(cnn, epochs=2 if FAST else 8)''',
         'Trains the CNN (about 2 min on a T4)', 'Eight epoch lines; val accuracy ends around 0.70–0.74; train accuracy runs ahead of val',
         'CUDA out of memory is very unlikely here; if it happens, Runtime → Restart and rerun', run=True),
    code(ESCAPE.format(raw=RAW, fname='cnn_cifar10.pt', model='cnn'),
         'Escape: load our trained CNN weights instead', 'Nothing unless USE_PRETRAINED = True; then accuracy ~0.77', '—'),

    md('''## 6 · Training it properly

### 6.1 · Reading the curves
Always plot **both** curves. Train loss falling while val loss rises = overfitting.'''),
    code('''def plot_curves(hists, names):
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for h, n in zip(hists, names):
        axes[0].plot(h["train_loss"], "--", label=f"{n} train"); axes[0].plot(h["val_loss"], label=f"{n} val")
        axes[1].plot(h["val_acc"], label=n)
    axes[0].set_title("loss (dashed = train)"); axes[1].set_title("validation accuracy")
    for a in axes: a.set_xlabel("epoch"); a.legend(fontsize=8)
    plt.show()
plot_curves([mlp_hist, cnn_hist], ["MLP", "CNN"])''',
         'Plots train/val loss and val accuracy for MLP vs CNN', 'Two plots; the CNN is clearly higher; CNN val loss flattens or rises while train loss keeps falling',
         'If you used the escape cells, the history is from the shorter run you did — that is fine'),
    md('''### 6.2 · Augmentation + dropout
Random crops and flips give a slightly different image every epoch; dropout switches off half the head's neurons during training. Both fight overfitting.'''),
    code('''@@ train_tf = transforms.Compose([transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip(), transforms.ToTensor(), normalize]) ||| train_tf = plain_tf  # TODO: Compose([RandomCrop(32, padding=4), RandomHorizontalFlip(), ToTensor(), normalize])
aug_train = Subset(torchvision.datasets.CIFAR10("data", train=True, download=False, transform=train_tf), range(n_train))
aug_loader = DataLoader(aug_train, batch_size=128, shuffle=True, num_workers=2)
print(train_tf)''',
         'TODO 4: the augmentation pipeline', 'The Compose printed with RandomCrop, RandomHorizontalFlip, ToTensor, Normalize',
         'Putting ToTensor before RandomCrop still works in new torchvision, but keep the order shown'),
    check('any(isinstance(t, transforms.RandomHorizontalFlip) for t in train_tf.transforms) and any(isinstance(t, transforms.RandomCrop) for t in train_tf.transforms)',
          'Augmentation pipeline has RandomCrop and RandomHorizontalFlip.', 'add RandomCrop(32, padding=4) and RandomHorizontalFlip() before ToTensor().'),
    code('''cnn_aug = SmallCNN(dropout=0.5).to(DEVICE)
aug_hist = fit(cnn_aug, epochs=2 if FAST else 12, loader=aug_loader)
plot_curves([cnn_hist, aug_hist], ["CNN", "CNN + aug + dropout"])''',
         'Trains the regularised CNN (about 3 min on a T4) and compares curves', 'Val accuracy ends around 0.76–0.80; train and val curves stay much closer together',
         'Takes longer per epoch because of augmentation on the CPU workers; that is expected', run=True),
    code(ESCAPE.format(raw=RAW, fname='cnn_aug_cifar10.pt', model='cnn_aug'),
         'Escape: load our trained augmented CNN', 'Nothing unless USE_PRETRAINED = True; then accuracy ~0.78', '—'),

    md('''### 6.3 · The confusion matrix
Rows = true class, columns = predicted class. The diagonal is correct; the off-diagonal shows **which** classes get confused.'''),
    code('''from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

@torch.no_grad()
def predict_all(model, loader):
    model.eval(); ys, ps = [], []
    for images, labels in loader:
        ps.append(model(images.to(DEVICE)).argmax(1).cpu()); ys.append(labels)
    return torch.cat(ys).numpy(), torch.cat(ps).numpy()

y_true, y_pred = predict_all(cnn_aug, test_loader)
@@ cm = confusion_matrix(y_true, y_pred) ||| cm = None  # TODO: build the confusion matrix with sklearn's confusion_matrix(y_true, y_pred)
if cm is not None:
    ConfusionMatrixDisplay(cm, display_labels=CLASSES).plot(xticks_rotation=45, cmap="Blues", colorbar=False)
    plt.gcf().set_size_inches(7, 6); plt.show()''',
         'TODO 5: confusion matrix of the augmented CNN', 'A 10 × 10 matrix; the biggest off-diagonal cells are cat ↔ dog and truck ↔ automobile',
         'Passing (y_pred, y_true) swaps rows and columns — the plot looks plausible but is transposed'),
    check('cm.shape == (10, 10) and cm.sum() == len(y_true)', 'Confusion matrix is 10 × 10 and covers every test image.',
          'confusion_matrix(y_true, y_pred)'),
    code('''per_class = cm.diagonal() / cm.sum(1)
for c, a in sorted(zip(CLASSES, per_class), key=lambda t: t[1]):
    print(f"{c:<12}{a:.2f}")
off = cm.copy(); np.fill_diagonal(off, 0)
i, j = np.unravel_index(off.argmax(), off.shape)
print(f"\\nMost common mistake: true {CLASSES[i]} predicted as {CLASSES[j]} ({off[i, j]} times)")''',
         'Per-class accuracy and the most common confusion', 'Lowest classes are usually cat and bird (~0.55–0.65); most common mistake e.g. "true cat predicted as dog"',
         '—'),

    md('''## 7 · Standing on giants: transfer learning

ResNet-18 was trained on 1.2 million ImageNet photos. We keep its backbone, replace the head with a 10-class layer, and fine-tune briefly. Images are upscaled to 96 × 96 so the pretrained filters see objects at a familiar size.'''),
    code('''from torchvision.models import resnet18, ResNet18_Weights
IMNET_MEAN, IMNET_STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
res_tf = transforms.Compose([transforms.Resize(96), transforms.RandomHorizontalFlip(), transforms.ToTensor(),
                             transforms.Normalize(IMNET_MEAN, IMNET_STD)])
res_test_tf = transforms.Compose([transforms.Resize(96), transforms.ToTensor(), transforms.Normalize(IMNET_MEAN, IMNET_STD)])
n_res = 5000 if FAST else 20000
res_train = Subset(torchvision.datasets.CIFAR10("data", train=True, transform=res_tf), range(n_res))
res_test = Subset(torchvision.datasets.CIFAR10("data", train=False, transform=res_test_tf), range(n_test))
res_loader = DataLoader(res_train, batch_size=128, shuffle=True, num_workers=2)
res_test_loader = DataLoader(res_test, batch_size=256, num_workers=2)

resnet = resnet18(weights=ResNet18_Weights.DEFAULT)
resnet.fc = nn.Linear(resnet.fc.in_features, 10)      # new head: 512 → 10
resnet = resnet.to(DEVICE)
print("new head:", resnet.fc)''',
         'Loads ImageNet ResNet-18 and swaps its head for 10 classes', 'new head: Linear(in_features=512, out_features=10, bias=True)',
         'Weights download (45 MB) can be slow on venue Wi-Fi', run=True),
    code('''opt = torch.optim.Adam(resnet.parameters(), lr=3e-4)
for ep in range(1 if FAST else 2):
    t0 = time.time()
    tl, ta = train_one_epoch(resnet, res_loader, opt)
    vl, va = evaluate(resnet, res_test_loader)
    print(f"epoch {ep+1}  train acc {ta:.3f} | val acc {va:.3f} | {time.time()-t0:.0f}s")
res_acc = va''',
         'Fine-tunes ResNet-18 on 20,000 images for 2 epochs (about 3 min on a T4)', 'val acc around 0.85–0.90 after 2 epochs — better than the CNN trained for 12',
         'CPU is very slow here (~10+ min even in FAST mode) → use the escape cell below', run=True),
    code('''# Escape hatch: if fine-tuning is too slow, freeze the backbone and train only the head for 1 epoch on 5,000 images
FREEZE_INSTEAD = False   # ← set to True and run this cell
if FREEZE_INSTEAD:
    for p in resnet.parameters(): p.requires_grad = False
    for p in resnet.fc.parameters(): p.requires_grad = True
    small = DataLoader(Subset(res_train, range(5000)), batch_size=128, shuffle=True, num_workers=2)
    tl, ta = train_one_epoch(resnet, small, torch.optim.Adam(resnet.fc.parameters(), lr=1e-3))
    res_acc = evaluate(resnet, res_test_loader)[1]
    print("frozen backbone, head only: val acc", round(res_acc, 3))''',
         'Escape: frozen backbone, head only (fast)', 'Nothing unless FREEZE_INSTEAD = True; then val acc ~0.70–0.78', '—'),
    code('''results = {"MLP": mlp_hist["val_acc"][-1], "Small CNN": cnn_hist["val_acc"][-1],
           "CNN + aug + dropout": aug_hist["val_acc"][-1], "ResNet-18 (pretrained)": res_acc}
for k, v in results.items():
    print(f"{k:<26}{v:.3f}  " + "█" * int(v * 40))''',
         'Summary table of all four models', 'Four bars, roughly MLP 0.50 < CNN 0.72 < CNN+aug 0.78 < ResNet-18 0.87', '—'),
    md('''### Tonight's deliverable
Write **one paragraph** in the cell below comparing the MLP, the CNN and the pretrained ResNet-18: the accuracy of each, and one observation from the confusion matrix (which classes get confused, and why you think so).'''),
    md('''*Your paragraph here.*''', 'Space for the deliverable paragraph'),

    md('''## Extra tasks (optional)

1. **Explode the learning rate:** train a fresh SmallCNN for 2 epochs with `lr=1.0`. What happens to the loss?
2. **Shuffle the pixels:** apply the same fixed random permutation to every image's pixels and retrain the MLP. Does its accuracy change? (Slide 1.64.)
3. **Forget `model.eval()`:** evaluate `cnn_aug` twice in train mode. Why do the two numbers differ?
4. **Count by formula:** compute the CNN's parameter count by hand with (k·k·C_in + 1)·C_out and check it equals 620,362.''', extra=True),
    code('''# Extra 1
boom = SmallCNN().to(DEVICE)
_ = fit(boom, epochs=2, lr=1.0)   # loss goes to ~2.30 (chance) or NaN: the steps overshoot''',
         'Extra 1 answer', 'Loss stuck near 2.30 or nan; accuracy ≈ 0.10', '—',
         unsolved='# Extra 1 — your code here (hint: fit(SmallCNN().to(DEVICE), epochs=2, lr=1.0))\n', extra=True),
    code('''# Extra 2
perm = torch.randperm(3 * 32 * 32)
class Shuffle(nn.Module):
    def forward(self, x): return x.flatten(1)[:, perm.to(x.device)]
mlp_shuf = nn.Sequential(Shuffle(), nn.Linear(3072, 512), nn.ReLU(), nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, 10)).to(DEVICE)
_ = fit(mlp_shuf, epochs=2)   # about the same accuracy as the normal MLP: it never used neighbourhoods''',
         'Extra 2 answer', 'Accuracy close to the unshuffled MLP', '—',
         unsolved='# Extra 2 — your code here (hint: a fixed torch.randperm(3072) applied after flattening)\n', extra=True),
    code('''# Extra 3
def eval_train_mode(model, loader):
    model.train(); c = t = 0
    with torch.no_grad():
        for im, lab in loader:
            c += (model(im.to(DEVICE)).argmax(1).cpu() == lab).sum().item(); t += len(lab)
    return c / t
print(eval_train_mode(cnn_aug, test_loader), eval_train_mode(cnn_aug, test_loader))  # dropout makes each run random''',
         'Extra 3 answer', 'Two slightly different accuracies, both lower than evaluate()', '—',
         unsolved='# Extra 3 — your code here (hint: call model.train() and evaluate the same model twice)\n', extra=True),
    code('''# Extra 4
convs = [(3, 3, 32), (3, 32, 64), (3, 64, 128)]
total = sum((k * k * cin + 1) * cout for k, cin, cout in convs) + (2048 * 256 + 256) + (256 * 10 + 10)
print(total, total == 620_362)''',
         'Extra 4 answer', '620362 True', '—',
         unsolved='# Extra 4 — your code here (hint: (k*k*C_in + 1) * C_out for each conv, plus the two Linear layers)\n', extra=True),
]
