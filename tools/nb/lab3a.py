from .common import md, code, check, how_to_use, gpu_check

META = dict(id='3A', file='Lab_3A', title='CLIP: zero-shot and search', day=3, block='Day 3 · B4 (finish at home)',
            goal='Embed images and text with CLIP, classify 300 photos with zero training, see how prompt wording changes accuracy, and build text → image and image → image search.',
            libs='transformers (CLIP), datasets, huggingface_hub', gpu=True)

CELLS = [
    how_to_use('3A', META['title'], META['goal'], 'Day 3 · Block 4 · Acts 3–4', 20),
    gpu_check('CPU (CLIP-B/32 is small; embedding 300 images takes about a minute)'),
    code('''import numpy as np, matplotlib.pyplot as plt
import torch.nn.functional as F
import transformers
from transformers import CLIPModel, CLIPProcessor
print("transformers", transformers.__version__)''',
         'Imports', 'transformers 5.x', '—'),

    md('''## The photos: a 300-image slice of Imagenette

Imagenette is a 10-class subset of ImageNet (tench, springer spaniel, cassette player, chain saw, church, French horn, garbage truck, gas pump, golf ball, parachute). We read the 160 px validation split straight from the Hugging Face Hub (`frgfm/imagenette`) and keep 30 photos per class. If the Hub is unreachable, the cell falls back to torchvision's own Imagenette download.'''),
    code('''from huggingface_hub import list_repo_files
from datasets import load_dataset
PER_CLASS = 10 if FAST else 30
CLASS_NAMES = ["tench", "English springer spaniel", "cassette player", "chain saw", "church",
               "French horn", "garbage truck", "gas pump", "golf ball", "parachute"]
try:
    files = [f for f in list_repo_files("frgfm/imagenette", repo_type="dataset")
             if f.startswith("160px/") and "valid" in f and f.endswith(".parquet")]
    raw = load_dataset("parquet", data_files=[f"hf://datasets/frgfm/imagenette/{f}" for f in files], split="train")
    pairs = [(ex["image"].convert("RGB"), ex["label"]) for ex in raw]
    print("loaded from the Hub:", files)
except Exception as e:
    print("Hub load failed, using torchvision instead:", e)
    import torchvision
    tv = torchvision.datasets.Imagenette("data", split="val", size="160px", download=True)
    pairs = [(tv[i][0].convert("RGB"), tv[i][1]) for i in range(len(tv))]

images, labels, count = [], [], {}
for im, lab in pairs:
    if count.get(lab, 0) < PER_CLASS:
        images.append(im); labels.append(lab); count[lab] = count.get(lab, 0) + 1
labels = np.array(labels)
print(len(images), "images |", np.bincount(labels).tolist(), "per class")''',
         'Loads 300 Imagenette photos (30 per class) from the Hub, with a torchvision fallback',
         'loaded from the Hub: [\'160px/validation/…parquet\'] · 300 images | [30, 30, …] per class',
         'If the parquet path changed, the fallback downloads 94 MB from fast.ai instead', run=True),
    code('''fig, axes = plt.subplots(2, 10, figsize=(16, 3.6))
for c in range(10):
    for row in range(2):
        idx = np.where(labels == c)[0][row]
        axes[row, c].imshow(images[idx]); axes[row, c].axis("off")
    axes[0, c].set_title(CLASS_NAMES[c], fontsize=8)
plt.show()''',
         'Shows two photos per class', 'A 2 × 10 grid: fish, dogs, cassette players, chainsaws, churches, horns, trucks, pumps, golf balls, parachutes', '—'),

    md('''## 3 · Embeddings and cosine similarity

An **embedding** is a vector that represents meaning; similar things get vectors pointing in similar directions. Cosine similarity measures that direction (slide 3.36).'''),
    code('''a, b, c = np.array([1, 2]), np.array([2, 4]), np.array([2, -1])
def cosine(u, v):
    @@ return u @ v / (np.linalg.norm(u) * np.linalg.norm(v)) ||| return 0.0  # TODO: dot product of u and v divided by the product of their lengths (np.linalg.norm)
print("cos(a, b) =", round(cosine(a, b), 3), "| cos(a, c) =", round(cosine(a, c), 3))''',
         'TODO 1: cosine similarity on the slide example', 'cos(a, b) = 1.0 | cos(a, c) = 0.0', 'Forgetting the norms gives 10 and 0 — a dot product, not a cosine'),
    check('abs(cosine(a, b) - 1) < 1e-9 and abs(cosine(a, c)) < 1e-9 and abs(cosine(np.array([1, 0]), np.array([1, 1])) - 2**-0.5) < 1e-9',
          'Cosine similarity matches slide 3.36.', 'u @ v / (np.linalg.norm(u) * np.linalg.norm(v))'),

    md('''## 4 · CLIP: images and words in one space

CLIP has an image encoder and a text encoder trained so that a photo and its caption land close together. We L2-normalise every embedding, so a dot product **is** the cosine similarity.

*Transformers v5 note:* `get_image_features` / `get_text_features` return an output object in v5 (the embedding is in `.pooler_output`) and a plain tensor in v4. The helper `as_tensor` handles both.'''),
    code('''CKPT = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(CKPT).to(DEVICE).eval()
processor = CLIPProcessor.from_pretrained(CKPT)

def as_tensor(out):
    return out if torch.is_tensor(out) else out.pooler_output

@torch.no_grad()
def embed_images(imgs, bs=64):
    feats = []
    for i in range(0, len(imgs), bs):
        inputs = processor(images=imgs[i:i + bs], return_tensors="pt").to(DEVICE)
        feats.append(as_tensor(model.get_image_features(**inputs)))
    return F.normalize(torch.cat(feats), dim=-1)

@torch.no_grad()
def embed_texts(texts):
    inputs = processor(text=texts, return_tensors="pt", padding=True).to(DEVICE)
    return F.normalize(as_tensor(model.get_text_features(**inputs)), dim=-1)

img_emb = embed_images(images)
print("image embeddings:", tuple(img_emb.shape), "| length of one vector:", round(float(img_emb[0].norm()), 3))''',
         'Loads CLIP ViT-B/32 and embeds all 300 images', 'image embeddings: (300, 512) | length of one vector: 1.0',
         'Shape (300, 50, 768) means you took last_hidden_state instead of the projected embedding — use get_image_features', run=True),

    md('''### 4.1 · Zero-shot classification
Write one sentence per class, embed them, and pick the sentence most similar to each image. No training at all.'''),
    code('''prompts = [f"a photo of a {c}." for c in CLASS_NAMES]
txt_emb = embed_texts(prompts)
@@ probs = (100 * img_emb @ txt_emb.T).softmax(dim=-1) ||| probs = torch.zeros(len(images), len(CLASS_NAMES), device=DEVICE)  # TODO: similarities × 100 (img_emb @ txt_emb.T), then softmax over classes (dim=-1)
pred = probs.argmax(1).cpu().numpy()
acc = (pred == labels).mean()
print(f"zero-shot accuracy: {acc:.3f}")
k = 0
print("image 0 top-3:", [(CLASS_NAMES[i], round(float(probs[k, i]), 3)) for i in probs[k].topk(3).indices.tolist()])''',
         'TODO 2: zero-shot probabilities from similarities', 'zero-shot accuracy around 0.95–0.99 and a confident top-3 for image 0 (tench)',
         'Without the ×100 (CLIP\'s learned temperature) the softmax is almost flat; accuracy stays the same but probabilities look useless'),
    check('probs.shape == (len(images), 10) and torch.allclose(probs.sum(1), torch.ones(len(images), device=probs.device), atol=1e-4) and acc > 0.8',
          'Zero-shot works: probabilities sum to 1 and accuracy is above 80%.', 'probs = (100 * img_emb @ txt_emb.T).softmax(dim=-1)'),

    md('''### 4.2 · Prompt wording matters
CLIP learned from captions, so talk to it like a caption. Compare bare class names, one template, and an **ensemble** that averages several templates.'''),
    code('''def zero_shot_acc(class_emb):
    return ((img_emb @ class_emb.T).argmax(1).cpu().numpy() == labels).mean()

bare = embed_texts(CLASS_NAMES)
templates = ["a photo of a {}.", "a close-up photo of a {}.", "a blurry photo of a {}.",
             "a photo of the {}, a type of object.", "a low resolution photo of a {}."]
per_template = [embed_texts([t.format(c) for c in CLASS_NAMES]) for t in templates]
@@ ens = F.normalize(torch.stack(per_template).mean(0), dim=-1) ||| ens = per_template[0]  # TODO: average the template embeddings (torch.stack(...).mean(0)) and normalise with F.normalize(..., dim=-1)
for name, e in [("bare class name", bare), ("'a photo of a …'", per_template[0]), ("ensemble of 5", ens)]:
    print(f"{name:<20}{zero_shot_acc(e):.3f}")''',
         'TODO 3: prompt ensembling; compares three prompt styles', 'Bare names a little lower, the template higher, the ensemble equal or slightly higher (differences of 1–3 points)',
         'Averaging without re-normalising shortens the vectors; argmax is unchanged here but the scores are no longer cosines'),
    check('ens.shape == (10, img_emb.shape[1]) and torch.allclose(ens.norm(dim=-1), torch.ones(10, device=ens.device), atol=1e-4)',
          'Ensemble embeddings have the right shape and unit length.', 'F.normalize(torch.stack(per_template).mean(0), dim=-1)'),

    md('''### 4.3 · Text → image search
Embed any sentence and rank all 300 photos by similarity to it.'''),
    code('''def show_results(idx, scores, title):
    fig, axes = plt.subplots(1, len(idx), figsize=(3 * len(idx), 3.3))
    for ax, i, s in zip(axes, idx, scores):
        ax.imshow(images[i]); ax.set_title(f"{s:.3f}", fontsize=9); ax.axis("off")
    fig.suptitle(title); plt.show()

query = "a parachute over the sea"
q = embed_texts([query])
scores = (img_emb @ q.T).squeeze(1)
@@ top = scores.topk(5).indices.tolist() ||| top = list(range(5))  # TODO: the indices of the 5 highest scores (scores.topk(5).indices)
show_results(top, scores[top].tolist(), f'"{query}"')''',
         'TODO 4: top-5 retrieval for a text query', 'Five parachute photos, ideally over water first, with similarity scores around 0.28–0.33',
         'Using argsort ascending returns the five worst matches'),
    check('top == scores.topk(5).indices.tolist()', 'Search returns the five best matches.', 'top = scores.topk(5).indices.tolist()'),
    code('''for query in ["a dog running on grass", "a red truck", "a person playing music", "something made of brass"]:
    s = (img_emb @ embed_texts([query]).T).squeeze(1)
    t = s.topk(5).indices.tolist()
    show_results(t, s[t].tolist(), f'"{query}"')''',
         'Runs four more text queries', 'Dogs on grass; red garbage trucks; French horns; brass horns — even though "brass" is not a class name', '—'),

    md('''### 4.4 · Image → image search
Use one photo's embedding as the query. No text involved.'''),
    code('''qi = int(np.where(labels == 4)[0][3])       # a church
s = (img_emb @ img_emb[qi]).cpu()
t = s.topk(6).indices.tolist()              # the first hit is the query itself
show_results(t, s[t].tolist(), "query = first image; the rest are its nearest neighbours")''',
         'Finds the nearest neighbours of one photo', 'The query church followed by five other churches, scores ~0.8–0.95', '—'),
    md('''### What CLIP cannot do
CLIP scores the **whole image** against a sentence. It is not a detector: it cannot tell you *where* the parachute is, and it is weak at counting and left/right (slide 3.50). Lab 3B adds boxes and masks.'''),

    md('''## Extra tasks (optional)

1. **Typographic attack:** write the word "church" in big letters on a photo of a golf ball and classify it again (slide 3.51).
2. **Counting:** compare the scores of "a photo of one dog" vs "a photo of three dogs" on the dog photos.
3. **SigLIP:** swap in `google/siglip-base-patch16-224` (use `AutoModel`/`AutoProcessor`, `padding="max_length"`) and compare the zero-shot accuracy.
4. **Few-shot:** label 5 photos per class, classify the rest by majority vote of the 3 nearest labelled embeddings (slide 3.40).''', extra=True),
    code('''# Extra 1
from PIL import ImageDraw, ImageFont
gi = int(np.where(labels == 8)[0][0]); attacked = images[gi].copy()
d = ImageDraw.Draw(attacked)
try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
except Exception: font = ImageFont.load_default()
d.rectangle([5, 50, 155, 100], fill="white"); d.text((10, 55), "church", fill="black", font=font)
e = embed_images([images[gi], attacked])
for name, row in zip(["original", "with text"], (100 * e @ txt_emb.T).softmax(-1)):
    print(name, CLASS_NAMES[int(row.argmax())], round(float(row.max()), 2))
plt.imshow(attacked); plt.axis("off"); plt.show()''',
         'Extra 1 answer', 'original: golf ball · with text: often church — the written word hijacks the prediction', '—',
         unsolved='# Extra 1 — your code here (hint: PIL.ImageDraw to write "church" on a golf-ball photo, then embed and compare)\n', extra=True),
    code('''# Extra 2
dogs = [images[i] for i in np.where(labels == 1)[0][:10]]
e = embed_images(dogs); t = embed_texts(["a photo of one dog.", "a photo of three dogs."])
print((e @ t.T).mean(0).tolist())   # nearly identical scores: CLIP barely counts''',
         'Extra 2 answer', 'Two nearly equal average scores', '—',
         unsolved='# Extra 2 — your code here\n', extra=True),
    code('''# Extra 3
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "sentencepiece"], check=False)   # SigLIP's tokenizer needs it
from transformers import AutoModel, AutoProcessor
sm = AutoModel.from_pretrained("google/siglip-base-patch16-224").to(DEVICE).eval()
sp = AutoProcessor.from_pretrained("google/siglip-base-patch16-224")
with torch.no_grad():
    ti = sp(text=prompts, padding="max_length", return_tensors="pt").to(DEVICE)
    te = F.normalize(as_tensor(sm.get_text_features(**ti)), dim=-1)
    ie = torch.cat([F.normalize(as_tensor(sm.get_image_features(**sp(images=images[i:i+32], return_tensors="pt").to(DEVICE))), dim=-1)
                    for i in range(0, len(images), 32)])
print("SigLIP zero-shot accuracy:", ((ie @ te.T).argmax(1).cpu().numpy() == labels).mean())''',
         'Extra 3 answer', 'SigLIP accuracy similar to or above CLIP', '—',
         unsolved='# Extra 3 — your code here\n', extra=True),
    code('''# Extra 4
rng = np.random.default_rng(0)
support = np.concatenate([rng.choice(np.where(labels == c)[0], 5, replace=False) for c in range(10)])
query_idx = np.setdiff1d(np.arange(len(images)), support)
sims = img_emb[query_idx] @ img_emb[support].T
nn3 = sims.topk(3, dim=1).indices.cpu().numpy()
votes = labels[support][nn3]
pred_fs = np.array([np.bincount(v, minlength=10).argmax() for v in votes])
print("5-shot kNN accuracy:", (pred_fs == labels[query_idx]).mean())''',
         'Extra 4 answer', '5-shot kNN accuracy around 0.9+', '—',
         unsolved='# Extra 4 — your code here\n', extra=True),
]
