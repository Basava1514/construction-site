from PIL import Image
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IMG_DIR = BASE / 'docs' / 'static' / 'images'

files = [
    'hero.webp',
    'svc1.webp', 'svc2.webp', 'svc3.webp',
    'proj1.webp', 'proj2.webp', 'proj3.webp',
]

IMG_DIR.mkdir(parents=True, exist_ok=True)

for name in files:
    src = IMG_DIR / name
    if not src.exists():
        print(f"Missing source: {src}")
        continue
    with Image.open(src) as im:
        # ensure RGB
        if im.mode in ('RGBA', 'LA'):
            bg = Image.new('RGB', im.size, (255,255,255))
            bg.paste(im, mask=im.split()[-1])
            im_rgb = bg
        else:
            im_rgb = im.convert('RGB')

        w, h = im_rgb.size
        # 2x -> original size (re-encode)
        out2 = IMG_DIR / name.replace('.webp', '@2x.webp')
        im_rgb.save(out2, 'WEBP', quality=80, method=6)
        print(f"Saved {out2} ({w}x{h})")

        # 1x -> half width (at least 320px)
        new_w = max(320, w // 2)
        new_h = int(h * (new_w / w))
        im1 = im_rgb.resize((new_w, new_h), Image.LANCZOS)
        out1 = IMG_DIR / name.replace('.webp', '@1x.webp')
        im1.save(out1, 'WEBP', quality=80, method=6)
        print(f"Saved {out1} ({new_w}x{new_h})")

print('Done')
