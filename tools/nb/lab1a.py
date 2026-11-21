from .common import md, code, check, how_to_use, gpu_check

META = dict(id='1A', file='Lab_1A', title='Images as arrays', day=1, block='Day 1 · B3 (finish tonight)',
            goal='Read an image as an array (shape, dtype, channels), fix the BGR bug, crop by slicing, threshold with a histogram, and write convolution by hand — then check it against OpenCV.',
            libs='NumPy, OpenCV, Pillow, scikit-image, Matplotlib', gpu=False)

CELLS = [
    how_to_use('1A', META['title'], META['goal'], 'Day 1 · Block 3 · Acts 2–3', 45, colab_gpu=False),
    gpu_check('the same settings (this lab is light)'),
    code('''import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import data

def show(*imgs, titles=None, cmap=None, size=4):
    """Show images side by side."""
    fig, axes = plt.subplots(1, len(imgs), figsize=(size * len(imgs), size))
    axes = np.atleast_1d(axes)
    for k, (ax, im) in enumerate(zip(axes, imgs)):
        ax.imshow(im, cmap=cmap if im.ndim == 2 else None, vmin=0 if im.ndim == 2 and im.dtype == np.uint8 else None,
                  vmax=255 if im.ndim == 2 and im.dtype == np.uint8 else None)
        ax.set_title(titles[k] if titles else "")
        ax.axis("off")
    plt.show()

print("NumPy", np.__version__, "| OpenCV", cv2.__version__)''',
         'Imports and a small show() helper', 'Two version lines, e.g. "NumPy 2.x | OpenCV 4.x"',
         'ModuleNotFoundError for skimage → run !pip install scikit-image'),

    md('''## 2 · Images are just numbers

An image is a grid of numbers. A grayscale image is a 2D table; a colour image stacks three tables (red, green, blue). The first thing you check about any image is its **shape** and its **dtype**.'''),
    code('''astronaut = data.astronaut()   # a colour photo, already RGB
camera = data.camera()         # a grayscale photo
print("astronaut:", astronaut.shape, astronaut.dtype, "min", astronaut.min(), "max", astronaut.max())
print("camera:   ", camera.shape, camera.dtype)
print("top-left pixel of astronaut (R, G, B):", astronaut[0, 0])
show(astronaut, camera, titles=["astronaut (H, W, 3)", "camera (H, W)"], cmap="gray")''',
         'Loads two built-in images and prints shape, dtype and range',
         'astronaut: (512, 512, 3) uint8 min 0 max 255 · camera: (512, 512) uint8 · two images shown',
         'Nothing downloads, so this rarely breaks; if skimage is old, `pip install -U scikit-image`'),
    md('''### 2.1 · Coordinates: `img[y, x]`, origin top-left

Rows come first (y grows **downward**), then columns (x grows to the right). Let us read one pixel and paint a small square so you can see where it is.'''),
    code('''marked = astronaut.copy()
y, x = 100, 300
print("pixel at row y=100, column x=300:", astronaut[y, x])
marked[y-10:y+10, x-10:x+10] = [255, 0, 0]      # paint a red square
show(marked, titles=["red square at y=100, x=300"])''',
         'Reads a pixel by [y, x] and paints a square there', 'A pixel value like [R G B] and the photo with a red square near the top right',
         'Writing img[x, y] silently paints the wrong place — swap to [y, x]'),

    md('''### 2.2 · Gotcha: BGR vs RGB

OpenCV loads images in **B, G, R** order. Matplotlib, PIL and PyTorch expect **R, G, B**. Below we save the photo and read it back with OpenCV, exactly as you would with your own files.'''),
    code('''cv2.imwrite("astronaut.png", cv2.cvtColor(astronaut, cv2.COLOR_RGB2BGR))   # save like any photo on disk
bgr = cv2.imread("astronaut.png")                                           # OpenCV gives B, G, R
show(bgr, titles=["read with cv2.imread — colours look wrong"])''',
         'Writes the photo to disk and reads it back with OpenCV', 'The astronaut with a blue face and an orange-blue flag (channels swapped)',
         'cv2.imread returns None if the path is wrong → check the file name'),
    code('''@@ rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) ||| rgb = None  # TODO: convert bgr to RGB with cv2.cvtColor(..., cv2.COLOR_BGR2RGB)
show(rgb, titles=["fixed"]) if rgb is not None else print("Fill in the TODO first")''',
         'TODO 1: convert BGR → RGB', 'The astronaut with normal skin colour', 'Using COLOR_RGB2BGR gives the same result here but is the wrong habit — use BGR2RGB'),
    check('np.array_equal(rgb, astronaut)', 'Colours fixed: rgb matches the original exactly.',
          'use cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).'),

    md('''### 2.3 · Cropping is just slicing

`img[y1:y2, x1:x2]` keeps rows y1 to y2 and columns x1 to x2. No function needed.'''),
    code('''@@ face = rgb[30:180, 150:300] ||| face = None  # TODO: crop rows 30–180 and columns 150–300 from rgb with slicing
show(face, titles=["face crop"]) if face is not None else print("Fill in the TODO first")''',
         'TODO 2: crop the face with slicing', 'A 150 × 150 crop of the astronaut\'s face', 'img[x1:x2, y1:y2] crops the wrong region with no error'),
    check('face.shape == (150, 150, 3)', 'Crop has shape (150, 150, 3).',
          'rows first: rgb[30:180, 150:300].'),

    md('''### 2.4 · Gotcha: uint8 overflow

A uint8 holds 0–255. What is 200 + 100? Predict it before you run the cell.'''),
    code('''a = np.array([200], dtype=np.uint8)
print("uint8: 200 + 100 =", (a + 100)[0], " ← wrapped around (300 - 256)")
safe = np.clip(a.astype(np.int16) + 100, 0, 255).astype(np.uint8)
print("fixed: convert, add, clip →", safe[0])

brighter_wrong = astronaut + 100
brighter_right = np.clip(astronaut.astype(np.int16) + 100, 0, 255).astype(np.uint8)
show(brighter_wrong, brighter_right, titles=["rgb + 100 (overflow)", "convert, add, clip"])''',
         'Shows 200 + 100 = 44 in uint8 and the fix', '"uint8: 200 + 100 = 44", "fixed → 255", then a glitchy image and a correctly brightened one',
         'NumPy 2 may warn about overflow for Python scalars; the array version above always shows the wrap'),

    md('''### 2.5 · Histogram and thresholding

A histogram counts how many pixels have each value. Thresholding turns a grayscale image into black and white: above T → 255, below → 0.'''),
    code('''plt.figure(figsize=(6, 3))
plt.hist(camera.ravel(), bins=256, range=(0, 255), color="gray")
plt.title("histogram of camera"); plt.xlabel("pixel value"); plt.ylabel("count")
plt.show()''',
         'Plots the histogram of the grayscale image', 'A histogram with a big dark peak (the coat) and a bright peak (the sky)', '—'),
    code('''T = 100
@@ binary = np.where(camera > T, 255, 0).astype(np.uint8) ||| binary = None  # TODO: 255 where camera > T, else 0 (np.where), as uint8
otsu_T, otsu = cv2.threshold(camera, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print("Otsu picked T =", otsu_T)
show(binary if binary is not None else camera, otsu, titles=[f"global T={T}", f"Otsu T={otsu_T:.0f}"], cmap="gray")''',
         'TODO 3: global threshold; Otsu picks T from the histogram', 'Otsu T around 100–105 and two black-and-white images',
         'Forgetting .astype(np.uint8) gives int64 — imshow still works but the check fails'),
    check('binary.dtype == np.uint8 and set(np.unique(binary)) <= {0, 255} and abs((binary == 255).mean() - (camera > 100).mean()) < 1e-9',
          'Threshold is correct: only 0 and 255, uint8.', 'np.where(camera > T, 255, 0).astype(np.uint8)'),

    md('''## 3 · Writing the rules by hand: convolution

**Convolution**: slide a small grid of weights (the kernel) over the image; at each position multiply the overlapping numbers and add them up. That sum is one output pixel. *Multiply, add, slide.*

First, the exact example from slide 1.41: an image whose rows are `0 0 0 9 9` and the kernel `-1 0 1`.'''),
    code('''img = np.array([[0, 0, 0, 9, 9]] * 5, dtype=np.float32)
kernel = np.array([[-1, 0, 1]] * 3, dtype=np.float32)

def conv2d(img, kernel):
    """Convolution by hand, no padding, stride 1 (the deep-learning kind: no kernel flip)."""
    kh, kw = kernel.shape
    H, W = img.shape
    out = np.zeros((H - kh + 1, W - kw + 1), dtype=np.float32)
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            @@ out[i, j] = np.sum(img[i:i+kh, j:j+kw] * kernel) ||| out[i, j] = 0  # TODO: multiply the patch img[i:i+kh, j:j+kw] by kernel and sum
    return out

result = conv2d(img, kernel)
print(result)''',
         'TODO 4: the multiply-and-add line inside convolution', '[[ 0. 27. 27.] × 3 rows] — the edge lights up', 'Using kernel.shape for out size gives the wrong size; it is H − kh + 1'),
    check('np.allclose(result, [[0, 27, 27]] * 3)', 'Matches the slide: every output row is 0 27 27.',
          'out[i, j] = np.sum(img[i:i+kh, j:j+kw] * kernel)'),
    md('''### 3.1 · Your convolution vs OpenCV

`cv2.filter2D` does the same multiply-add-slide (it pads the border, so we compare the inside only). Your loop is slow in Python; OpenCV is fast C++ — same maths.'''),
    code('''import time
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
cam = camera.astype(np.float32)
t0 = time.time(); mine = conv2d(cam, sobel_x); t_mine = time.time() - t0
t0 = time.time(); ocv = cv2.filter2D(cam, -1, sobel_x)[1:-1, 1:-1]; t_ocv = time.time() - t0
print(f"same result: {np.allclose(mine, ocv, atol=1e-3)} | yours {t_mine:.2f}s vs OpenCV {t_ocv*1000:.1f}ms")
show(np.abs(mine), titles=["Sobel-x: vertical edges"], cmap="gray")''',
         'Runs your conv2d and cv2.filter2D on a real photo and compares', '"same result: True | yours ~2–4 s vs OpenCV ~1 ms" and an edge image',
         'If False, your TODO 4 line is wrong; if very slow on CPU, wait — it is a 510 × 510 Python loop'),

    md('''### 3.2 · The kernel gallery

Same operation, different numbers, completely different results. A kernel gives a large output where the image looks like the kernel.'''),
    code('''kernels = {
    "box blur": np.ones((3, 3), np.float32) / 9,
    "gaussian": cv2.getGaussianKernel(5, 1.2) @ cv2.getGaussianKernel(5, 1.2).T,
    "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32),
    "sobel-x": sobel_x,
    "sobel-y": sobel_x.T,
}
outs = [np.clip(np.abs(cv2.filter2D(cam, -1, k)), 0, 255).astype(np.uint8) for k in kernels.values()]
show(*outs, titles=list(kernels), cmap="gray", size=3)''',
         'Applies five classic kernels to the same photo', 'Five images: blurred, smoother blur, sharper, vertical edges, horizontal edges', '—'),
    md('''### 3.3 · Edge strength

Sobel-x finds vertical edges, Sobel-y horizontal ones. The edge strength combines both: √(gx² + gy²).'''),
    code('''gx = cv2.filter2D(cam, -1, sobel_x)
gy = cv2.filter2D(cam, -1, sobel_x.T)
@@ mag = np.sqrt(gx**2 + gy**2) ||| mag = None  # TODO: edge strength = square root of (gx squared + gy squared)
canny = cv2.Canny(camera, 100, 200)
show(mag if mag is not None else cam, canny, titles=["edge strength", "Canny"], cmap="gray")''',
         'TODO 5: edge magnitude; Canny for comparison', 'A bright outline of the photographer and tripod, and thin white Canny edges', 'Using gx + gy instead of the square root gives cancelling edges'),
    check('mag.shape == cam.shape and np.allclose(mag, np.hypot(gx, gy))', 'Edge strength is correct.',
          'mag = np.sqrt(gx**2 + gy**2)'),
    md('''### Done with the core lab 🎉

You can now read any image as an array, avoid the three classic gotchas (BGR, `[y, x]`, uint8 overflow) and explain convolution with your own code. Tonight's deliverable: finish this notebook and Lab 1B.'''),

    md('''## Extra tasks (optional)

1. **HSV colour masking:** find the red parts of the astronaut photo with one range on Hue.
2. **Histogram equalisation:** make a dark version of `camera` and fix it with `cv2.equalizeHist`.
3. **Morphology:** clean the noisy binary mask with an opening (erosion then dilation).
4. **Resizing:** shrink a mask with nearest vs bilinear interpolation and count how many new values appear.''', extra=True),
    code('''# Extra 1 — red pixels via Hue
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
red = (((h < 10) | (h > 170)) & (s > 100) & (v > 60)).astype(np.uint8) * 255
show(rgb, red, titles=["photo", "red mask"], cmap="gray")''',
         'Extra 1 answer: hue range mask', 'A mask that lights up the red parts of the flag and suit badges', 'OpenCV hue runs 0–179, not 0–359',
         unsolved='# Extra 1 — your code here (hint: cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV), red hue is near 0 and near 179)\n', extra=True),
    code('''# Extra 2 — equalisation
dark = (camera * 0.3).astype(np.uint8)
eq = cv2.equalizeHist(dark)
show(dark, eq, titles=["dark", "equalised"], cmap="gray")''',
         'Extra 2 answer: equalizeHist', 'A dark image and a contrast-restored one', '—',
         unsolved='# Extra 2 — your code here (hint: multiply camera by 0.3, then cv2.equalizeHist)\n', extra=True),
    code('''# Extra 3 — opening removes specks
rng = np.random.default_rng(0)
noisy = otsu.copy(); noisy[rng.random(noisy.shape) < 0.03] = 255
opened = cv2.morphologyEx(noisy, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
show(noisy, opened, titles=["noisy mask", "opened"], cmap="gray")''',
         'Extra 3 answer: morphological opening', 'Speckled mask, then a clean mask', '—',
         unsolved='# Extra 3 — your code here (hint: cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)))\n', extra=True),
    code('''# Extra 4 — masks must be resized with nearest
mask = np.zeros((100, 100), np.uint8); mask[20:60, 30:80] = 1; mask[60:90, 10:50] = 2
near = cv2.resize(mask, (37, 37), interpolation=cv2.INTER_NEAREST)
bil = cv2.resize(mask.astype(np.float32), (37, 37), interpolation=cv2.INTER_LINEAR)
print("nearest values:", np.unique(near), "| bilinear distinct values:", len(np.unique(bil)))''',
         'Extra 4 answer: nearest vs bilinear on a label mask', '"nearest values: [0 1 2] | bilinear distinct values: dozens"', '—',
         unsolved='# Extra 4 — your code here (hint: cv2.resize with INTER_NEAREST vs INTER_LINEAR, then np.unique)\n', extra=True),
]
