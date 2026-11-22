# Slides — Day 1 · From pixels to features

Computer Vision for Developers · SDAIA Academy · Sun 22 Nov 2026

## How to read this file
- One `###` heading = one slide. Never merge two slides. Never split one slide. The slide count at the bottom must match the built deck.
- `Type` tells the builder which layout to use: `title`, `section`, `definition`, `compare` (X vs Y), `cards` (3–6 numbered cards), `rule`, `worked` (worked example with numbers), `diagram`, `table`, `code`, `list`, `activity`, `quiz`.
- `Screen` is exactly what appears on the slide. `Notes` are presenter notes (1–3 speakable sentences). `[STRETCH]` and `(cut first)` appear in notes only, never on screen.
- Footer on every slide: `SECTION LABEL · Day 1 · NN / TOTAL`.

---

## Opening

### 1.01 · Computer Vision for Developers
Type: title
Screen: SDAIA ACADEMY · Computer Vision for Developers · Day 1 — From pixels to features · 3 days · 22–24 November 2026 · Instructor: Musa Ibn Rashid
Notes: Welcome everyone. Over three days we go from "what is a pixel" to models that find anything you can describe in words.

### 1.02 · About me
Type: cards
Screen: Musa Ibn Rashid · Software Engineering (AI Focus), KFUPM · KAUST AI Training Graduate · AI Instructor, SDAIA Academy · QA Engineer, voice-AI startup
Notes: Keep it to thirty seconds. The point is that I build this stuff, not only teach it.

### 1.03 · Let's meet each other first
Type: activity
Screen: Introductions · Your name · Major, university and year · Where you are in tech: what you have built or worked on · About 30 seconds each
Notes: Go first so they hear the length: name, major, university, year, what you work on. Then go around the room, about 30 seconds each. Note shared interests out loud; they are the first hint for project teams.

### 1.04 · Before we start: the pre-test
Type: activity
Screen: 20 questions · 15 minutes · Not graded — it shows what you already know · Open the course site → Pre-test
Notes: Tell them guessing is fine; we compare with the post-test on Day 3 to see how far they moved.

### 1.05 · What this course is
Type: cards
Screen: 1 · How machines turn pixels into meaning · 2 · Concepts first, then code you can read line by line · 3 · Colab labs every day — solved and unsolved versions · 4 · Activities, a project, and an exam
Notes: Every topic answers a problem. If you ever ask "why are we learning this", the answer is on the previous slide.

### 1.06 · Three days, one story
Type: table
Screen: Day 1 · From pixels to features · How does a machine see at all? | Day 2 · Where is it, what shape is it, where is it going? · Find, outline, count, follow | Day 3 · Seeing beyond labels · Learn without labels, understand words
Notes: The course is one story: teaching a machine to see. Each fix creates the next problem.

### 1.07 · Today, in seven acts
Type: list
Screen: Act 1 · The seeing problem · Act 2 · Images are just numbers · Act 3 · Writing the rules by hand · Act 4 · Learning from data — and why the obvious network fails · Act 5 · The convolutional neural network · Act 6 · Training it properly · Act 7 · Standing on giants
Notes: Morning is foundations, afternoon is the real machinery. By 3 o'clock you will have trained a CNN.

### 1.08 · Goals for today
Type: cards
Screen: 01 · Explain why vision is hard for a computer · 02 · Read an image as an array: shape, dtype, channels · 03 · Apply a convolution by hand · 04 · Explain why an MLP fails on images · 05 · Trace shapes and count parameters in a CNN · 06 · Diagnose a training run from its curves · 07 · Explain residual connections and transfer learning
Notes: Goals 5 and 6 are what the exam tests hardest.

### 1.09 · The course project
Type: cards
Screen: A vision system for a real problem · Teams of 2–3 · GitHub repo · Built at night · 5-minute presentation on Day 3 · Brief and rubric are on the site now
Notes: Show the project page for two minutes. Ask them to form teams by the end of the day; people who mentioned similar work in the introductions are a good start.

### 1.10 · How you are graded
Type: table
Screen: Project build · 60 | Presentation · 10 | Theory exam (Day 3 morning) · 30 | Deploy bonus · +5 (max 100)
Notes: The exam covers Days 1 and 2. Evidence — numbers, curves, failure images — is what earns build marks.

---

## Act 1 · The seeing problem

### 1.11 · Act 1
Type: section
Screen: 01 · The seeing problem · Why something a baby does effortlessly took computers 50 years
Notes: Start with the problem, not the solution.

### 1.12 · What is computer vision?
Type: definition
Screen: Computer vision — teaching computers to extract meaning from images and video: what is there, where it is, and what is happening. · Image processing: image in → image out · Computer vision: image in → meaning out · Computer graphics: description in → image out
Notes: The difference between the three is what goes in and what comes out. Vision is the hard direction.

### 1.13 · Computer vision is everywhere
Type: cards
Screen: Phone face unlock · Traffic enforcement cameras · Pipeline corrosion inspection · Crowd management at large events · Medical scan screening · Crop and palm-tree disease detection
Notes: Ask the room which of these they used today. Most will say face unlock.

### 1.14 · The semantic gap
Type: compare
Screen: What you see · "A cat on a sofa" | What the computer sees · 224 × 224 × 3 = 150,528 numbers between 0 and 255 · The gap between these two is the whole field.
Notes: Write 150,528 on the board. Everything we do this week is about closing this gap.

### 1.15 · Why seeing is hard — 1
Type: cards
Screen: 01 · Viewpoint — the same car from the front and the side shares almost no pixels · 02 · Lighting — noon and dusk change every number · 03 · Scale — near and far objects differ in size by 10×
Notes: Every one of these changes the numbers completely while the meaning stays the same.

### 1.16 · Why seeing is hard — 2
Type: cards
Screen: 04 · Occlusion — half the object is hidden · 05 · Deformation — a cat can be any shape · 06 · Clutter — the object blends into the background · 07 · Intra-class variation — "chair" covers thousands of designs
Notes: A good vision system must survive all seven at once.

### 1.17 · The question for the whole course
Type: rule
Screen: How do we turn a grid of numbers into meaning — reliably, under all seven of these conditions?
Notes: Keep this question on the board all three days.

---

## Act 2 · Images are just numbers

### 1.18 · Act 2
Type: section
Screen: 02 · Images are just numbers · Before a machine can see, we need to know exactly what it receives
Notes: This act is where most real-world bugs come from. Go slowly.

### 1.19 · The pixel
Type: definition
Screen: Pixel — the smallest unit of an image: one position holding one number (gray) or three numbers (color). · Zoom into any photo far enough and you reach a grid of squares.
Notes: Show the zoom from a face to a grid of squares.

### 1.20 · Grayscale = a 2D grid
Type: worked
Screen: A 5 × 5 grayscale image is a 5 × 5 table of numbers · 0 = black · 255 = white · values in between = grays · shape = (5, 5)
Notes: Why 255? One byte holds 256 values, 0 to 255. That type is called uint8.

### 1.21 · Color = three channels
Type: diagram
Screen: Red channel · Green channel · Blue channel → stacked → one color image · shape = (H, W, 3) · Pure red = (255, 0, 0) · White = (255, 255, 255) · Black = (0, 0, 0)
Notes: A color image is three grayscale images stacked. Each channel is how much of that color is at each pixel.

### 1.22 · Shape is the first thing you check
Type: table
Screen: Grayscale photo · (480, 640) | Color photo · (480, 640, 3) | Color photo with transparency · (480, 640, 4) | Batch of 32 color photos · (32, 480, 640, 3)
Notes: Before you do anything with an image, print its shape. Half of all vision bugs are shape bugs.

### 1.23 · Coordinates: the origin is top-left
Type: diagram
Screen: (0, 0) top-left corner · x grows to the right · y grows downward · img[row, col] = img[y, x]
Notes: This is the opposite of school graphs where y goes up. Slide 1.24 is the bug this causes.

### 1.24 · Gotcha: x and y swapped
Type: code
Screen: `crop = img[50:150, 200:400]` → rows 50–150 (y), columns 200–400 (x) · Writing `img[x1:x2, y1:y2]` crops the wrong region — and no error is raised.
Notes: No error, just a wrong crop. Silent bugs are the worst kind.

### 1.25 · Data types: uint8 vs float
Type: compare
Screen: uint8 · whole numbers 0–255 · how images are stored on disk · small and fast | float32 · decimals, usually scaled to 0–1 · how neural networks want their input · precise
Notes: Models want floats around 0 to 1. Converting is called normalising.

### 1.26 · Gotcha: uint8 overflow
Type: worked
Screen: Brighten a pixel: 200 + 100 = ? · In uint8: 300 does not fit → wraps around → 44 · The bright pixel turns dark. · Fix: convert to a larger type, add, then clip to 0–255.
Notes: Ask the room to predict the answer before revealing 44. 300 minus 256 is 44.

### 1.27 · Gotcha: BGR vs RGB
Type: compare
Screen: OpenCV loads images as B, G, R · Matplotlib, PIL, PyTorch expect R, G, B · Result: blue faces and orange skies · Fix: `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`
Notes: This is the single most common bug in vision code. You will see it in Lab 1A on purpose.

### 1.28 · Resolution and aspect ratio
Type: cards
Screen: Resolution — how many pixels (width × height) · Aspect ratio — width ÷ height (4:3, 16:9) · Models usually need a fixed size, e.g. 224 × 224 · Squashing to a square distorts shapes; padding keeps them
Notes: When you resize a 16:9 photo to a square, a round wheel becomes an oval. Sometimes that matters.

### 1.29 · Resizing needs interpolation
Type: compare
Screen: Nearest neighbour · copy the closest pixel · blocky, fast, keeps exact values (use for masks) | Bilinear · average the 4 nearest pixels · smooth, standard for photos
Notes: Use nearest for label masks so class numbers never get averaged into nonsense like class 2.5.

### 1.30 · Other color spaces: HSV
Type: compare
Screen: RGB · how much red, green, blue | HSV · Hue (which color) · Saturation (how strong) · Value (how bright) · "Find the red object" = one range on Hue — even in shadow.
Notes: In RGB, a red object in shadow has totally different numbers. In HSV the hue barely changes.

### 1.31 · Files vs arrays
Type: compare
Screen: JPEG · small, lossy, block artifacts, good for photos | PNG · larger, lossless, supports transparency, good for masks and diagrams · Once loaded, both are just arrays.
Notes: Never save segmentation masks as JPEG; compression changes the class values at edges.

### 1.32 · How models receive images
Type: compare
Screen: PyTorch · (N, C, H, W) — channels first | NumPy / OpenCV / TensorFlow · (N, H, W, C) — channels last · `ToTensor()` changes the order and divides by 255
Notes: N is the batch size, how many images go in together. Know which layout your library expects.

### 1.33 · Pixel Detective
Type: activity
Screen: Activity · Pixel Detective · A grid of numbers slowly reveals an image · First team to name it wins · Site → Activities → Pixel Detective
Notes: Ten minutes. The point: the computer starts with only the numbers.

---

## Act 3 · Classical image processing — writing the rules by hand

### 1.34 · Act 3
Type: section
Screen: 03 · Writing the rules by hand · For decades, people designed every step of vision manually
Notes: This act is history, but the core operation — convolution — is the heart of everything that follows.

### 1.35 · Point operations
Type: cards
Screen: Brightness · add a constant to every pixel · Contrast · multiply every pixel · Inversion · 255 − pixel · Each output pixel depends on one input pixel only
Notes: Point operations look at one pixel at a time and nothing else.

### 1.36 · The histogram
Type: definition
Screen: Histogram — a bar chart of how many pixels have each value (0–255). · Dark image → bars piled on the left · Washed-out image → bars squeezed in the middle
Notes: A histogram tells you about lighting without looking at the picture.

### 1.37 · Histogram equalisation
Type: compare
Screen: Before · values squeezed into 40–120 · details hidden | After · values stretched across 0–255 · details visible · Used for X-rays, night footage, scanned documents
Notes: It spreads the values out so small differences become visible.

### 1.38 · Thresholding
Type: definition
Screen: Thresholding — turning a grayscale image into black and white: every pixel above T becomes 255, every pixel below becomes 0. · Global · one T for the whole image · Adaptive · a different T for each neighbourhood · Otsu · picks T automatically from the histogram
Notes: Adaptive thresholding is how phone scanner apps handle a page with a shadow across it.

### 1.39 · Neighbourhood operations
Type: rule
Screen: Point operations ignore neighbours. But meaning lives in neighbourhoods — an edge is a difference between a pixel and the pixel next to it.
Notes: To see edges and textures, an output pixel must depend on a small patch of input pixels.

### 1.40 · Convolution
Type: definition
Screen: Convolution — slide a small grid of weights (the kernel) over the image; at each position multiply the overlapping numbers and add them up. That sum is one output pixel.
Notes: Multiply, add, slide. Say it three times. This one operation powers the rest of Day 1 and all of Day 2.

### 1.41 · Convolution by hand — the setup
Type: worked
Screen: Image (5 × 5): every row is 0 0 0 9 9 · Kernel (3 × 3): every row is −1 0 1 · Output size with no padding: 3 × 3
Notes: The image has a vertical edge between the dark left and the bright right. Watch what the kernel does to it.

### 1.42 · Convolution by hand — the result
Type: worked
Screen: Position 1 (columns 1–3): (0·−1 + 0·0 + 0·1) × 3 rows = 0 · Position 2 (columns 2–4): (0·−1 + 0·0 + 9·1) × 3 = 27 · Position 3 (columns 3–5): (0·−1 + 9·0 + 9·1) × 3 = 27 · Output row: 0 27 27 → the kernel lights up where the edge is
Notes: Flat regions give zero, edges give big numbers. The kernel is an edge detector.

### 1.43 · A kernel is a pattern detector
Type: rule
Screen: A kernel gives a large output where the image looks like the kernel, and near zero where it does not.
Notes: This sentence explains CNNs. Keep it on the board.

### 1.44 · The kernel gallery
Type: table
Screen: Box blur · all 1/9 · averages neighbours | Gaussian blur · centre-heavy weights · smooth, natural blur | Sharpen · centre 5, sides −1 · exaggerates differences | Sobel-x · −1 0 1 / −2 0 2 / −1 0 1 · vertical edges | Sobel-y · Sobel-x rotated · horizontal edges
Notes: Lab 1A runs every one of these on a real photo.

### 1.45 · Edges
Type: cards
Screen: Edge = where brightness changes sharply · Gradient = how fast it changes (Sobel-x and Sobel-y) · Edge strength = √(gx² + gy²) · Canny: blur → gradient → thin the edges → keep strong ones and their connected weak ones
Notes: Canny is still used today in robotics and document processing because it is fast and needs no training.

### 1.46 · Morphology — cleaning masks
Type: cards
Screen: Erosion · shrinks white regions, removes specks · Dilation · grows white regions, fills small holes · Opening = erosion then dilation · Closing = dilation then erosion
Notes: (cut first) Useful for cleaning thresholded masks. One slide is enough.

### 1.47 · Hand-crafted features
Type: cards
Screen: Corners · points where edges meet — stable to track · HOG · a histogram of edge directions in each cell — the classic pedestrian detector · SIFT · describes a keypoint so it can be matched across photos despite scale and rotation
Notes: Engineers spent years designing these. They were the state of the art until 2012.

### 1.48 · The classic pipeline
Type: diagram
Screen: Image → hand-designed features (HOG, SIFT) → classifier (e.g. SVM) → label · Humans design step 2 · The machine only learns step 3
Notes: The important part — what to look at — was decided by a human.

### 1.49 · Where the hand-written rules break
Type: cards
Screen: New lighting → thresholds fail · New viewpoint → features stop matching · New class → an expert must design new features · Every task needs months of manual engineering
Notes: The rules were brittle. That brings us to the key question of the day.

### 1.50 · The question that changed the field
Type: rule
Screen: If a kernel is just a grid of numbers… could the machine learn the numbers itself, from examples?
Notes: Yes. That is a convolutional neural network. But first we need to understand learning.

### 1.51 · Be the Kernel
Type: activity
Screen: Activity · Be the Kernel · Apply a 3 × 3 kernel to a patch by hand · Fastest correct team wins · Site → Activities → Be the Kernel
Notes: Ten minutes. Then launch Lab 1A and get everyone to the end of the "convolution by hand" section before lunch.

### 1.52 · Lab 1A — Images as arrays
Type: list
Screen: Load and inspect: shape, dtype, channels · Fix the BGR bug · Crop with slicing · Histogram and thresholding · Convolution by hand in NumPy → compare with OpenCV · Extra tasks at the end
Notes: The unsolved notebook has TODOs with checks that print a green tick. Finish it tonight if you don't get through it.

---

## Act 4 · Learning from data — and why the obvious network fails

### 1.53 · Act 4
Type: section
Screen: 04 · Learning from data · Instead of writing rules, show the machine examples
Notes: After lunch, the machine starts learning.

### 1.54 · Rules vs learning
Type: compare
Screen: Traditional programming · rules + data → answers | Machine learning · data + answers → rules
Notes: In machine learning we give examples with the right answers and the computer finds the rules.

### 1.55 · Supervised learning in one picture
Type: diagram
Screen: Image + label ("cat") → model → prediction ("dog, 70%") → loss: how wrong? → adjust the weights → repeat thousands of times
Notes: That loop is all of training. Everything else is detail.

### 1.56 · Train, validation, test
Type: cards
Screen: Training set · the model learns from it · Validation set · you tune choices with it · Test set · sealed until the end — the honest score · Typical split: 70 / 15 / 15
Notes: If you peek at the test set while tuning, your final number is a lie. This rule is in your project rubric.

### 1.57 · Loss
Type: definition
Screen: Loss — one number that says how wrong the model is on an example. Training means making this number small.
Notes: High loss, bad model. The whole of training is pushing this number down.

### 1.58 · Gradient descent
Type: diagram
Screen: Picture the loss as a hilly landscape · The weights are your position · The gradient tells you which way is uphill · Take a small step downhill · Repeat
Notes: You are blindfolded on a mountain; you feel the slope with your feet and step down.

### 1.59 · The learning rate
Type: compare
Screen: Too small · tiny steps, training takes forever | Just right · steady progress to the bottom | Too big · overshoots, loss jumps around or explodes
Notes: The learning rate is the most important single setting in deep learning. Lab 1B has an extra task where you set it to 1.0 and watch it explode.

### 1.60 · From scores to probabilities: softmax
Type: worked
Screen: Raw scores: cat 2.0 · dog 1.0 · car 0.1 → softmax → cat 0.66 · dog 0.24 · car 0.10 · Always positive, always sum to 1
Notes: Softmax turns any list of scores into probabilities.

### 1.61 · Cross-entropy loss
Type: worked
Screen: True class: cat · Model says cat 0.66 → loss = −log(0.66) ≈ 0.42 · Model says cat 0.05 → loss = −log(0.05) ≈ 3.0 · Confidently wrong is punished hardest
Notes: Cross-entropy looks only at the probability given to the correct class.

### 1.62 · The obvious attempt: an MLP
Type: diagram
Screen: Flatten the image into one long list → fully connected layers (every input connected to every neuron) → softmax · Called a multilayer perceptron (MLP)
Notes: This is what anyone would try first. Let's see why it fails.

### 1.63 · Failure 1: parameter explosion
Type: worked
Screen: Input 224 × 224 × 3 = 150,528 numbers · First layer of 1,000 neurons → 150,528 × 1,000 ≈ 150 million weights · in the first layer alone · More weights → more data needed → overfits easily
Notes: That is one layer. A real network needs many.

### 1.64 · Failure 2: no sense of neighbourhood
Type: rule
Screen: Shuffle all the pixels of every image the same way — the MLP learns exactly as well. It never knew which pixels were neighbours.
Notes: For an MLP, pixel 1 and pixel 2 are no more related than pixel 1 and pixel 50,000. But neighbours are where edges live.

### 1.65 · Failure 3: move the cat, start again
Type: compare
Screen: Cat in the top-left · learned by weights connected to the top-left | Same cat in the bottom-right · completely different weights — must be learned again
Notes: An MLP must learn "cat" separately at every position. That is a huge waste.

### 1.66 · What we actually need
Type: cards
Screen: 01 · Local — look at small neighbourhoods · 02 · Shared — use the same detector everywhere · 03 · Hierarchical — combine small patterns into big ones
Notes: Local plus shared is exactly what a kernel does. Act 5 builds the network from it.

---

## Act 5 · The convolutional neural network

### 1.67 · Act 5
Type: section
Screen: 05 · The convolutional neural network · Act 3's kernels, but learned from data
Notes: Climb starts here. Everything from now builds on convolution.

### 1.68 · A convolution layer
Type: definition
Screen: Convolution layer — a set of kernels whose numbers are learned during training. Each kernel produces one feature map showing where its pattern appears.
Notes: Same multiply-add-slide as Act 3. The only difference is that training picks the numbers.

### 1.69 · Local connectivity + weight sharing
Type: compare
Screen: MLP neuron · connected to all 150,528 inputs | Conv neuron · connected to a 3 × 3 patch · the same 9 weights reused at every position
Notes: These two ideas are why CNNs need far fewer weights and recognise an object anywhere in the image.

### 1.70 · Convolution on a color image
Type: diagram
Screen: Input 32 × 32 × 3 · kernel 3 × 3 × 3 (depth matches the input channels) · one kernel → one 32 × 32 feature map · 64 kernels → 64 feature maps → output 32 × 32 × 64
Notes: The kernel always spans all input channels. The number of kernels sets the number of output channels.

### 1.71 · Counting parameters
Type: worked
Screen: Formula: (k × k × C_in + 1) × C_out · Example: 3 × 3 kernels, 3 input channels, 64 kernels → (3·3·3 + 1) × 64 = 1,792 · The + 1 is the bias, one per kernel
Notes: Compare 1,792 with the 150 million from slide 1.63. Same input, a hundred thousand times fewer weights.

### 1.72 · Padding
Type: compare
Screen: No padding ("valid") · output shrinks · 32 → 30 with a 3 × 3 kernel | Zero padding of 1 ("same") · add a border of zeros · 32 → 32 · edges get processed properly
Notes: Without padding, every layer eats a border and edge pixels are barely seen.

### 1.73 · Stride
Type: definition
Screen: Stride — how many pixels the kernel jumps each step. Stride 1 visits every position; stride 2 skips every other one and halves the output size.
Notes: Stride 2 is a cheap way to shrink the image as we go deeper.

### 1.74 · Dilation
Type: definition
Screen: Dilated convolution — spread the kernel's taps apart so a 3 × 3 kernel covers a 5 × 5 area with no extra weights.
Notes: (cut first) Mainly used in segmentation for a wider view. One slide is enough.

### 1.75 · The output size formula
Type: rule
Screen: Output = ⌊(W − K + 2P) / S⌋ + 1 · W input size · K kernel size · P padding · S stride
Notes: This formula is in the exam and in Shape Race. Write it down.

### 1.76 · Output size — three worked cases
Type: worked
Screen: W 32, K 3, P 1, S 1 → (32 − 3 + 2)/1 + 1 = 32 · W 32, K 3, P 0, S 1 → (32 − 3)/1 + 1 = 30 · W 32, K 3, P 1, S 2 → ⌊31 / 2⌋ + 1 = 16
Notes: Do the third one with them slowly. The floor is where people slip.

### 1.77 · Pooling
Type: compare
Screen: Max pooling · keep the largest value in each 2 × 2 window · "was the pattern here at all?" | Average pooling · keep the mean · smoother · Both: 2 × 2 with stride 2 halves height and width, no weights to learn
Notes: Max pooling keeps the strongest response and throws away exactly where it was. That gives a little shift tolerance.

### 1.78 · Why we need activations
Type: rule
Screen: Stacking linear layers gives… one linear layer. Without a non-linearity, a 50-layer network is no smarter than a 1-layer network.
Notes: Two multiplications in a row are still just a multiplication. Non-linearity is what lets depth help.

### 1.79 · ReLU
Type: definition
Screen: ReLU(x) = max(0, x) · negatives become 0, positives pass through · simple, fast, and trains well in deep networks
Notes: ReLU is one of the reasons deep CNNs suddenly worked in 2012. Act 7 comes back to it.

### 1.80 · The classifier head
Type: diagram
Screen: Feature maps → flatten → fully connected layers → 10 scores → softmax → probabilities · The conv layers find patterns; the head decides the class
Notes: The body sees, the head decides. Transfer learning in Act 7 swaps only the head.

### 1.81 · Tracing shapes through a small CNN
Type: table
Screen: Input · 3 × 32 × 32 | Conv 3→32, k3 p1 + ReLU · 32 × 32 × 32 | MaxPool 2 · 32 × 16 × 16 | Conv 32→64, k3 p1 + ReLU · 64 × 16 × 16 | MaxPool 2 · 64 × 8 × 8 | Conv 64→128, k3 p1 + ReLU · 128 × 8 × 8 | MaxPool 2 · 128 × 4 × 4 | Flatten · 2,048 | FC → 256 → 10 · 10 scores
Notes: This is the model in Lab 1B. Trace it with them line by line; the exam has a question exactly like this.

### 1.82 · Counting that network's parameters
Type: worked
Screen: Conv1 (27 + 1) × 32 = 896 · Conv2 (288 + 1) × 64 = 18,496 · Conv3 (576 + 1) × 128 = 73,856 · FC1 2,048 × 256 + 256 = 524,544 · FC2 256 × 10 + 10 = 2,570 · Total ≈ 620 K · An MLP on the same images (3,072 → 512 → 256 → 10) ≈ 1.7 M
Notes: Notice where the parameters live: the first fully connected layer has most of them. The CNN has fewer weights and will be more accurate. Lab 1B proves it.

### 1.83 · What the layers learn
Type: diagram
Screen: Layer 1 · edges and color blobs → Layer 2 · textures and corners → Layer 3 · parts (eyes, wheels) → Deep layers · whole objects
Notes: Nobody programmed this hierarchy. It emerges from training, and it looks like Act 3's hand-made kernels in the first layer.

### 1.84 · Receptive field
Type: definition
Screen: Receptive field — the region of the original image that one neuron can "see". It grows with every layer.
Notes: A neuron deep in the network sees a big area even though each kernel is only 3 by 3.

### 1.85 · Receptive field — worked
Type: worked
Screen: One 3 × 3 conv · sees 3 × 3 · Two stacked 3 × 3 convs · sees 5 × 5 · Three stacked 3 × 3 convs · sees 7 × 7 · Pooling and stride make it grow much faster
Notes: Each extra 3 by 3 layer adds two pixels of view. This is why depth matters.

### 1.86 · Shape Race
Type: activity
Screen: Activity · Shape Race · Given a stack of layers, predict the output shape · One formula, many layers · Site → Activities → Shape Race
Notes: Eight minutes. Anyone who learned slide 1.75 can win.

---

## Act 6 · Training it properly

### 1.87 · Act 6
Type: section
Screen: 06 · Training it properly · A good architecture trained badly is a bad model
Notes: This is where the practical skill lives.

### 1.88 · Batches, epochs, iterations
Type: cards
Screen: Batch · a group of images processed together (e.g. 64) · Iteration · one weight update, from one batch · Epoch · one full pass through the training set · 50,000 images ÷ 64 per batch ≈ 782 iterations per epoch
Notes: CIFAR-10 has 50,000 training images, so that number is real for Lab 1B.

### 1.89 · The DataLoader
Type: diagram
Screen: Dataset (images + labels) → transforms (resize, to tensor, normalise, augment) → DataLoader (shuffles, batches) → model
Notes: The DataLoader is a conveyor belt that hands the model one shuffled batch at a time.

### 1.90 · The training loop, line by line
Type: code
Screen: `for images, labels in loader:` · `outputs = model(images)` — forward · `loss = loss_fn(outputs, labels)` — how wrong · `optimizer.zero_grad()` — clear old gradients · `loss.backward()` — compute gradients · `optimizer.step()` — update weights
Notes: Five lines. Forgetting zero_grad makes gradients pile up across batches — a classic silent bug.

### 1.91 · Reading learning curves
Type: compare
Screen: Underfitting · train and val loss both high · model too simple or not trained long enough | Good fit · both low and close together | Overfitting · train loss keeps falling, val loss starts rising · the model memorises
Notes: Always plot both curves. One curve tells you nothing.

### 1.92 · Overfitting, explained
Type: definition
Screen: Overfitting — the model memorises the training examples, including their noise, instead of learning patterns that work on new images.
Notes: Like a student who memorised last year's exam answers and fails when the questions change.

### 1.93 · Fixes for overfitting
Type: cards
Screen: More data · the best fix if you can get it · Augmentation · fake new data from old · Dropout · randomly switch off neurons in training · Early stopping · stop when val loss stops improving · Weight decay · keep weights small
Notes: Try more data and augmentation first. They usually help most.

### 1.94 · Data augmentation
Type: cards
Screen: Flip · Random crop · Rotation · Color jitter · Blur · Each epoch the model sees a slightly different version of each image
Notes: Augmentation teaches invariance: a flipped cat is still a cat.

### 1.95 · Gotcha: augmentation that lies
Type: compare
Screen: Safe · flipping cats, cars, X-ray texture | Wrong · flipping digits (6 ↔ 9), text, left/right road signs · Ask: does this change the true label?
Notes: Augmentation must never change the correct answer.

### 1.96 · Dropout
Type: definition
Screen: Dropout — during training, randomly set a fraction of neurons (e.g. 50%) to zero each step. The network cannot rely on any single neuron.
Notes: Like a team where any member might be absent, so everyone has to know the job.

### 1.97 · Batch normalisation
Type: definition
Screen: BatchNorm — rescale each layer's outputs to a steady range (mean 0, spread 1) using the current batch, then let the network adjust with two learned numbers. Training becomes faster and more stable.
Notes: Keep it intuitive: it keeps the numbers flowing between layers in a healthy range.

### 1.98 · Gotcha: train mode vs eval mode
Type: compare
Screen: `model.train()` · dropout on · BatchNorm uses batch statistics | `model.eval()` · dropout off · BatchNorm uses saved statistics · Forget `model.eval()` and predictions change randomly
Notes: Always call model.eval() and use torch.no_grad() before testing or predicting. This is in Spot the Bug.

### 1.99 · Classification metrics
Type: cards
Screen: Accuracy · correct ÷ total · Precision · of everything I called "sick", how many were sick? · Recall · of all the sick, how many did I find? · F1 · balance of precision and recall
Notes: Precision is about false alarms, recall is about misses.

### 1.100 · Why accuracy lies
Type: worked
Screen: 100 X-rays · 95 healthy · 5 sick · A model that always says "healthy" → accuracy 95% · recall for "sick" = 0 of 5 = 0% · Useless, with a great-looking number
Notes: On imbalanced data, always report precision and recall per class.

### 1.101 · The confusion matrix
Type: diagram
Screen: Rows = true class · columns = predicted class · diagonal = correct · off-diagonal = which classes get confused (e.g. cat ↔ dog, truck ↔ car)
Notes: The confusion matrix tells you which mistakes the model makes, not only how many.

### 1.102 · Reproducibility
Type: cards
Screen: Set seeds for Python, NumPy and PyTorch · GPUs can still give slightly different numbers run to run · Record library versions · A 1% "improvement" may just be seed noise
Notes: Before you celebrate a small gain, run it again with a different seed.

### 1.103 · Run discipline
Type: rule
Screen: Change one thing at a time. Log every run: what you changed, the numbers, the curve. Save the best checkpoint.
Notes: This is how professionals work, and it is what the project's evidence marks reward.

---

## Act 7 · Standing on giants: architectures and transfer learning

### 1.104 · Act 7
Type: section
Screen: 07 · Standing on giants · Every famous architecture is the fix for a problem the previous one had
Notes: Ceiling block. Tell it as a chain of problems and fixes.

### 1.105 · ImageNet
Type: cards
Screen: 1.2 million labelled training images · 1,000 classes · The yearly competition (ILSVRC) that drove the field from 2010 to 2017
Notes: A huge labelled dataset made deep learning possible. Day 3 asks what happens when labels are too expensive.

### 1.106 · LeNet (1998)
Type: cards
Screen: Problem · read handwritten digits on cheques · Fix · conv → pool → conv → pool → fully connected · Small, worked, but computers were too weak to go bigger
Notes: The CNN idea is old. What was missing was data and compute.

### 1.107 · AlexNet (2012): why that year?
Type: cards
Screen: Data · ImageNet · Compute · trained on GPUs · ReLU · trains much faster than older activations · Dropout · fights overfitting · Error dropped by about 10 points in one year
Notes: Three ingredients arrived at once. This is the moment deep learning took over vision.

### 1.108 · VGG (2014): just go deeper
Type: worked
Screen: Idea · use only 3 × 3 convs, stack many · Two 3 × 3 layers see 5 × 5 (like one 5 × 5) · weights: 2 × 9 = 18 per channel pair vs 25 · plus an extra ReLU · Fewer weights, more non-linearity
Notes: Small kernels stacked beat big kernels. That idea is still used everywhere.

### 1.109 · Inception (2014): many sizes at once
Type: cards
Screen: Problem · objects appear at many sizes · Fix · run 1 × 1, 3 × 3 and 5 × 5 convs in parallel and stack the results · 1 × 1 convs shrink channels first to keep it cheap
Notes: (cut first) The 1 × 1 convolution trick returns in MobileNet.

### 1.110 · The degradation problem
Type: rule
Screen: Researchers made networks deeper — and training accuracy got worse. Not overfitting. The deeper network simply could not learn.
Notes: This surprised everyone. A deeper network could at least copy the shallow one and add layers that do nothing, yet training could not find that.

### 1.111 · ResNet (2015): skip connections
Type: diagram
Screen: Output = F(x) + x · The block only has to learn the change ("residual"), not the whole thing · If a layer is useless, it can learn F(x) = 0 and pass x straight through · Enabled 50, 101, 152 layers
Notes: Learn the change, not the whole thing. ResNet is still the default backbone in many systems, including Day 2's detectors.

### 1.112 · Why skip connections help training
Type: cards
Screen: The signal has a shortcut forward · The gradient has a shortcut backward · Deep networks become as easy to train as shallow ones
Notes: The shortcut lets the learning signal reach the early layers without fading away.

### 1.113 · MobileNet: the phone problem
Type: rule
Screen: ResNet-50 is too heavy for a phone or a camera chip. How do we keep accuracy and cut the computation?
Notes: Real products run on small devices. Cost becomes the problem.

### 1.114 · Depthwise-separable convolution
Type: compare
Screen: Standard conv · each kernel mixes space and all channels at once | Depthwise-separable · Step 1 depthwise: one 3 × 3 filter per channel (space only) · Step 2 pointwise: 1 × 1 convs mix the channels
Notes: Split one expensive job into two cheap jobs.

### 1.115 · The cost, worked
Type: worked
Screen: Cost ratio ≈ 1/C_out + 1/K² · K = 3, C_out = 256 → 1/256 + 1/9 ≈ 0.115 · About 8.7× fewer multiplications · with a small accuracy drop
Notes: This is a ceiling slide. The 1 over K squared term dominates, so 3 by 3 kernels give roughly 8 to 9 times savings.

### 1.116 · EfficientNet: scale wisely
Type: cards
Screen: Deeper · more layers · Wider · more channels · Higher resolution · bigger input · Scale all three together by a fixed ratio → B0 to B7
Notes: (cut first) Scaling only one dimension wastes compute.

### 1.117 · Architectures at a glance
Type: table
Screen: LeNet · it works · 1998 | AlexNet · data + GPU + ReLU · 2012 | VGG · deep 3 × 3 stacks · 2014 | Inception · multi-scale · 2014 | ResNet · skip connections · 2015 | MobileNet · cheap convs for phones · 2017 | EfficientNet · balanced scaling · 2019
Notes: Read the middle column: each one fixed a problem the previous one had.

### 1.118 · Transfer learning
Type: definition
Screen: Transfer learning — reuse a network trained on a huge dataset (like ImageNet) as a starting point for your own task, instead of starting from random weights.
Notes: The early layers learned edges and textures that are useful for almost any image.

### 1.119 · Freeze or fine-tune?
Type: compare
Screen: Freeze the backbone · train only a new head · fast, works with little data | Fine-tune everything · small learning rate · best when you have more data or your images look different from ImageNet
Notes: Start frozen. Unfreeze when you have data and time.

### 1.120 · Choosing a strategy
Type: table
Screen: Little data, similar images · freeze, train the head | Little data, different images (X-ray, satellite) · freeze most, fine-tune the last blocks | Lots of data, similar · fine-tune all | Lots of data, different · fine-tune all, or train from scratch
Notes: Your project will almost certainly use row one or two.

### 1.121 · What CNNs still can't do
Type: cards
Screen: Local view · global context arrives late · Fixed classes · can only answer with the classes it was trained on · Hungry for labels · ImageNet took years to label
Notes: Hold these three. Day 3 opens with them.

### 1.122 · Lab 1B — Your first CNN
Type: list
Screen: CIFAR-10 · MLP baseline → small CNN → print shapes per layer → augmentation + dropout → curves + confusion matrix → pretrained ResNet-18 · Tonight: one paragraph comparing the three
Notes: Start it now and run the MLP vs CNN cells together. The rest is tonight's work.

### 1.123 · Spot the Bug
Type: activity
Screen: Activity · Spot the Bug · Five real vision bugs · Find what is wrong and why · Teams race
Notes: [STRETCH] Twenty minutes. Only use it if you are ahead. Bugs: BGR shown as RGB, uint8 overflow, swapped x/y crop, eval mode forgotten, test data used for tuning.

---

## Close of Day 1

### 1.124 · Eight distinctions to remember
Type: table
Screen: Image processing vs computer vision · image out vs meaning out | uint8 vs float32 · storage vs model input | BGR vs RGB · OpenCV vs everything else | Point vs neighbourhood operation · one pixel vs a patch | Hand-crafted vs learned features | MLP vs CNN · global weights vs local shared kernels | Underfitting vs overfitting | Freeze vs fine-tune
Notes: Read them aloud. Each one is a likely exam question.

### 1.125 · Day 1 recap
Type: list
Screen: Vision is hard: seven reasons · An image is an array of numbers · A kernel detects the pattern it looks like · MLPs fail on images; CNNs fix it with local, shared kernels · Shapes and parameters can be computed by formula · Read both curves before you trust a model · Residuals made depth trainable; transfer learning reuses it
Notes: Seven lines, the whole day.

### 1.126 · Exit ticket
Type: quiz
Screen: 1 · What is the shape of a 640 × 480 color photo in NumPy? · 2 · Why does 200 + 100 give 44? · 3 · Output size: W 64, K 3, P 1, S 2? · 4 · Train loss falls, val loss rises — what is happening? · 5 · What does a skip connection let a block learn?
Notes: Answers: (480, 640, 3) · uint8 wraps at 256 · 32 · overfitting · only the change (the residual).

### 1.127 · Tonight
Type: list
Screen: Finish Lab 1A and Lab 1B · Form your team · Submit your project idea on the site · Read the project rubric
Notes: Remind them the project is built at night.

### 1.128 · Tomorrow — Day 2
Type: title
Screen: Where is it, what shape is it, where is it going? · Detection · Segmentation · Tracking
Notes: Today the model answered "what". Tomorrow it answers "where" and "which one".

---
Total slides: 128
