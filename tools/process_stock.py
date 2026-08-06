from PIL import Image
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / 'docs' / 'static' / 'images' / 'stock_raw'
OUT = BASE / 'docs' / 'static' / 'images'
LOGO = OUT / 'logo.webp'

OUT.mkdir(parents=True, exist_ok=True)

files = sorted([p for p in RAW.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png')])
if not files:
    print('No stock files found in', RAW)

# Helper to ensure RGB
def to_rgb(im):
    if im.mode in ('RGBA','LA'):
        bg = Image.new('RGB', im.size, (255,255,255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert('RGB')

# process each file
for i, src in enumerate(files, start=1):
    name = src.stem
    with Image.open(src) as im:
        im_rgb = to_rgb(im)
        w,h = im_rgb.size
        # save @2x as original size encoded to webp
        out2 = OUT / f'stock_{i}@2x.webp'
        im_rgb.save(out2, 'WEBP', quality=85, method=6)
        print('Saved', out2, 'size', im_rgb.size)
        # save @1x as half width (min 320)
        new_w = max(320, w//2)
        new_h = int(h * (new_w / w))
        im1 = im_rgb.resize((new_w, new_h), Image.LANCZOS)
        out1 = OUT / f'stock_{i}@1x.webp'
        im1.save(out1, 'WEBP', quality=80, method=6)
        print('Saved', out1, 'size', im1.size)

# Composite logo onto the first image to create hero merged images
if files and LOGO.exists():
    hero2 = OUT / 'stock_1@2x.webp'
    hero1 = OUT / 'stock_1@1x.webp'
    if hero2.exists() and hero1.exists():
        with Image.open(hero2) as h2, Image.open(LOGO) as logo:
            h2 = to_rgb(h2)
            logo = to_rgb(logo)
            # scale logo to 20% width of hero
            hw, hh = h2.size
            lw = int(hw * 0.20)
            lw = min(lw, 300)
            lh = int(logo.size[1] * (lw / logo.size[0]))
            logo_resized = logo.resize((lw, lh), Image.LANCZOS)
            # position bottom-right with padding
            pad = int(hw * 0.03)
            x = hw - logo_resized.size[0] - pad
            y = hh - logo_resized.size[1] - pad
            # draw semi-opaque white rounded rectangle behind logo
            from PIL import ImageDraw
            draw = ImageDraw.Draw(h2)
            rect_x0 = x - 12
            rect_y0 = y - 8
            rect_x1 = x + logo_resized.size[0] + 12
            rect_y1 = y + logo_resized.size[1] + 8
            # rounded rect fallback: draw rectangle with slight transparency
            overlay = Image.new('RGBA', h2.size, (255,255,255,0))
            od = ImageDraw.Draw(overlay)
            od.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(255,255,255,200))
            h2 = Image.alpha_composite(h2.convert('RGBA'), overlay)
            h2.paste(logo_resized, (x,y), logo_resized.convert('RGBA'))
            out_merged2 = OUT / 'hero_merged@2x.webp'
            h2.convert('RGB').save(out_merged2, 'WEBP', quality=85, method=6)
            print('Saved merged hero', out_merged2)
        # create 1x merged by resizing merged2
        with Image.open(out_merged2) as m2:
            mw, mh = m2.size
            new_mw = max(320, mw//2)
            new_mh = int(mh * (new_mw / mw))
            m1 = m2.resize((new_mw, new_mh), Image.LANCZOS)
            out_merged1 = OUT / 'hero_merged@1x.webp'
            m1.convert('RGB').save(out_merged1, 'WEBP', quality=80, method=6)
            print('Saved merged hero', out_merged1)
    else:
        print('Hero source missing, cannot composite')
else:
    print('No logo or stock files to composite; logo exists?', LOGO.exists())

print('Done')
