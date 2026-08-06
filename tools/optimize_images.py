from PIL import Image
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ATT = Path(r"C:\Users\NCNY1134\.copilot\attachments")
OUT = BASE / 'docs' / 'static' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

mapping = {
    '9fde9dc9-375d-46f9-8533-8ca3e755b85c-Image (4).jpg': ('logo.webp', (400, 200)),
    'b01fd754-a417-48d6-b36a-02b324e2a789-Image (3).jpg': ('hero.webp', (1600, 800)),
    'aeac5c46-4525-4d62-947d-bfadac767f2d-Image (9).jpg': ('svc1.webp', (1200, 800)),
    '4e754625-7b7d-4548-a6e3-8246d45fe1b4-Image (7).jpg': ('svc2.webp', (1200, 800)),
    '35829314-44f7-446c-b91a-3f63427d7bc9-e3962406-5b8c-462e-a093-387ebc363de8-clipboard.png': ('svc3.webp', (1200,800)),
    '1d0c721e-2fd9-4bd5-8292-dc127c25c589-Image (5).jpg': ('proj1.webp', (1200,800)),
    '5fbf4910-da88-4b95-bc68-50ff7a39cf13-Image (6).jpg': ('proj2.webp', (1200,800)),
    '78499900-51ed-4c68-86f3-35764e5bd08c-Image (2).jpg': ('proj3.webp', (1200,800)),
    '819a097c-c532-4d71-a7d5-16281eebfc55-Image (1).jpg': ('gallery1.webp', (1200,800)),
    '133ea124-e768-42c8-b283-fd8e3b131ff9-Image (8).jpg': ('gallery2.webp', (1200,800)),
}

for src_name, (out_name, size) in mapping.items():
    src = ATT / src_name
    if not src.exists():
        print(f"Source not found: {src}")
        continue
    with Image.open(src) as im:
        # Convert to RGB if needed
        if im.mode in ('RGBA', 'LA'):
            bg = Image.new('RGB', im.size, (255,255,255))
            bg.paste(im, mask=im.split()[-1])
            im2 = bg
        else:
            im2 = im.convert('RGB')
        # Resize preserving aspect ratio to fit within size
        im2.thumbnail(size, Image.LANCZOS)
        out_path = OUT / out_name
        im2.save(out_path, 'WEBP', quality=80, method=6)
        print(f"Saved {out_path} (size {im2.size})")
print('Done')
