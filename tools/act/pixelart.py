"""Ten 24 x 24 grayscale pixel-art images for Pixel Detective.

Each picture is drawn with simple shapes on a 240 x 240 canvas and
averaged down to 24 x 24, giving a grid of numbers 0-255 (0 = black,
255 = white). The result is stored as plain number arrays in the page.
"""
from PIL import Image, ImageDraw

S = 240
BG = 238


def canvas():
    im = Image.new('L', (S, S), BG)
    return im, ImageDraw.Draw(im)


def done(im):
    small = im.resize((24, 24), Image.BOX)
    px = list(small.getdata())
    return [px[r * 24:(r + 1) * 24] for r in range(24)]


def cup():
    im, d = canvas()
    d.rectangle([50, 90, 160, 200], fill=60)
    d.ellipse([140, 110, 205, 175], outline=60, width=16)
    d.rectangle([40, 200, 175, 214], fill=110)
    for x in (75, 105, 135):
        d.line([x, 75, x - 8, 50, x, 25], fill=150, width=7)
    return done(im)


def car():
    im, d = canvas()
    d.rounded_rectangle([20, 110, 220, 165], 18, fill=55)
    d.polygon([(60, 110), (85, 70), (165, 70), (190, 110)], fill=55)
    d.polygon([(78, 106), (95, 80), (122, 80), (122, 106)], fill=190)
    d.polygon([(130, 106), (130, 80), (158, 80), (175, 106)], fill=190)
    for cx in (65, 175):
        d.ellipse([cx - 25, 145, cx + 25, 195], fill=20)
        d.ellipse([cx - 10, 160, cx + 10, 180], fill=160)
    return done(im)


def cat_face():
    im, d = canvas()
    d.polygon([(45, 95), (60, 25), (110, 70)], fill=70)
    d.polygon([(195, 95), (180, 25), (130, 70)], fill=70)
    d.ellipse([40, 55, 200, 215], fill=70)
    d.ellipse([75, 105, 105, 140], fill=225); d.ellipse([135, 105, 165, 140], fill=225)
    d.ellipse([85, 112, 97, 136], fill=10); d.ellipse([145, 112, 157, 136], fill=10)
    d.polygon([(108, 158), (132, 158), (120, 172)], fill=200)
    for y in (165, 180):
        d.line([30, y, 95, 170], fill=200, width=3); d.line([210, y, 145, 170], fill=200, width=3)
    return done(im)


def palm_tree():
    im, d = canvas()
    d.line([125, 225, 118, 160, 112, 100, 118, 70], fill=80, width=18)
    for x0, y0, x1, y1 in [(118, 70, 30, 110), (118, 70, 210, 105), (118, 70, 50, 40), (118, 70, 190, 35), (118, 70, 120, 15)]:
        d.line([x0, y0, (x0 + x1) // 2, min(y0, y1) - 15, x1, y1], fill=40, width=16)
    d.ellipse([20, 205, 220, 245], fill=170)
    return done(im)


def mosque_dome():
    im, d = canvas()
    d.rectangle([45, 140, 195, 215], fill=90)
    d.pieslice([55, 50, 185, 230], 180, 360, fill=50)
    d.line([120, 50, 120, 20], fill=50, width=6)
    d.ellipse([108, 6, 132, 30], fill=50); d.ellipse([114, 4, 136, 26], fill=BG)
    d.rectangle([200, 70, 222, 215], fill=70); d.polygon([(198, 70), (211, 35), (224, 70)], fill=70)
    d.rounded_rectangle([105, 165, 135, 215], 12, fill=200)
    return done(im)


def key():
    im, d = canvas()
    d.ellipse([20, 80, 100, 160], outline=50, width=20)
    d.rectangle([95, 110, 220, 130], fill=50)
    d.rectangle([180, 130, 195, 165], fill=50); d.rectangle([205, 130, 220, 155], fill=50)
    return done(im)


def phone():
    im, d = canvas()
    d.rounded_rectangle([70, 15, 170, 225], 20, fill=35)
    d.rectangle([82, 40, 158, 190], fill=190)
    d.ellipse([110, 198, 130, 218], fill=150)
    d.line([105, 27, 135, 27], fill=120, width=4)
    return done(im)


def house():
    im, d = canvas()
    d.polygon([(20, 115), (120, 25), (220, 115)], fill=40)
    d.rectangle([45, 110, 195, 220], fill=95)
    d.rectangle([100, 150, 140, 220], fill=30)
    d.rectangle([60, 130, 88, 158], fill=210); d.rectangle([152, 130, 180, 158], fill=210)
    d.rectangle([160, 40, 180, 85], fill=40)
    return done(im)


def fish():
    im, d = canvas()
    d.ellipse([40, 70, 180, 170], fill=60)
    d.polygon([(165, 120), (225, 70), (225, 170)], fill=60)
    d.polygon([(90, 75), (120, 40), (140, 80)], fill=90)
    d.ellipse([65, 100, 85, 120], fill=230); d.ellipse([71, 106, 81, 116], fill=10)
    d.arc([100, 85, 150, 155], 300, 60, fill=150, width=5)
    return done(im)


def star():
    import math
    im, d = canvas()
    pts = []
    for k in range(10):
        r = 105 if k % 2 == 0 else 42
        a = math.pi / 2 + k * math.pi / 5
        pts.append((120 + r * math.cos(a), 125 - r * math.sin(a)))
    d.polygon(pts, fill=45)
    return done(im)


IMAGES = [
    ('cup', 'a cup', cup), ('car', 'a car', car), ('cat face', 'a cat face', cat_face),
    ('palm tree', 'a palm tree', palm_tree), ('mosque dome', 'a mosque dome', mosque_dome),
    ('key', 'a key', key), ('phone', 'a phone', phone), ('house', 'a house', house),
    ('fish', 'a fish', fish), ('star', 'a star', star),
]


def all_images():
    return [{'name': n, 'label': l, 'px': f()} for n, l, f in IMAGES]
