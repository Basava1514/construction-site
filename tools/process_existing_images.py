#!/usr/bin/env python3
"""
Use existing user-uploaded images to create gallery and composited hero.
- Composite logo onto first suitable image to create hero_merged
- Generate @1x/@2x variants for all images
- Create a comprehensive gallery display
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'docs' / 'static' / 'images'
LOGO = OUT / 'logo.webp'

OUT.mkdir(parents=True, exist_ok=True)

def to_rgb(im):
    """Convert image to RGB, handling transparency."""
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        if im.mode == 'P':
            im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
        return bg
    return im.convert('RGB')

print("=" * 70)
print("Processing existing images: creating hero composite + srcset variants")
print("=" * 70)

# Find all existing WebP images (user-uploaded)
images = []
for img_file in sorted(OUT.glob('*.webp')):
    if '@' not in img_file.name and 'logo' not in img_file.name and 'stock' not in img_file.name:
        images.append(img_file)

print(f"Found {len(images)} existing images to process")
for img in images:
    print(f"  - {img.name}")

# Generate responsive variants for each image
print("\n" + "=" * 70)
print("STEP 1: Creating @1x/@2x variants for all existing images")
print("=" * 70)

variants_created = 0
hero_src = None

for src in images:
    i = src.stem.lower()
    try:
        with Image.open(src) as im:
            im_rgb = to_rgb(im)
            w, h = im_rgb.size
            
            # Skip if already a variant
            if '@' in src.name:
                print(f"  Skipping {src.name} (already a variant)")
                continue
            
            # Save @2x (original size as WebP)
            out2 = OUT / f'{src.stem}@2x.webp'
            if out2.exists():
                print(f"  {src.stem}@2x.webp exists; skipping")
            else:
                im_rgb.save(out2, 'WEBP', quality=85, method=6)
                print(f"  Saved {src.stem}@2x.webp ({w}x{h}, {out2.stat().st_size/1024:.1f}KB)")
                variants_created += 1
            
            # Save @1x (half width, min 320px)
            out1 = OUT / f'{src.stem}@1x.webp'
            if out1.exists():
                print(f"  {src.stem}@1x.webp exists; skipping")
            else:
                new_w = max(320, w // 2)
                new_h = int(h * (new_w / w))
                im1 = im_rgb.resize((new_w, new_h), Image.LANCZOS)
                im1.save(out1, 'WEBP', quality=80, method=6)
                print(f"  Saved {src.stem}@1x.webp ({new_w}x{new_h}, {out1.stat().st_size/1024:.1f}KB)")
                variants_created += 1
            
            # Use the first sizeable image as hero source
            if hero_src is None and w >= 800 and h >= 450:
                hero_src = src
    except Exception as e:
        print(f"  ERROR processing {src}: {e}")

# Step 2: Composite logo onto an image to create hero_merged
print("\n" + "=" * 70)
print("STEP 2: Creating composited hero with company logo overlay")
print("=" * 70)

if not hero_src:
    print("  No suitable image found for hero composite. Using largest image...")
    sizes = [(img, Image.open(img).size) for img in images]
    hero_src = max(sizes, key=lambda x: x[1][0] * x[1][1])[0]

if hero_src and LOGO.exists():
    try:
        print(f"Using {hero_src.name} as hero base")
        with Image.open(hero_src) as h2, Image.open(LOGO) as logo:
            h2_rgb = to_rgb(h2)
            logo_rgb = to_rgb(logo)
            
            # Resize hero to standard dimensions if needed
            hw, hh = h2_rgb.size
            target_w = 1600
            if hw > target_w:
                target_h = int(hh * (target_w / hw))
                h2_rgb = h2_rgb.resize((target_w, target_h), Image.LANCZOS)
                hw, hh = h2_rgb.size
            
            print(f"  Hero dimensions: {hw}x{hh}")
            print(f"  Logo dimensions: {logo_rgb.size}")
            
            # Scale logo to 15-18% of hero width
            lw = max(80, min(300, int(hw * 0.16)))
            lh = int(logo_rgb.size[1] * (lw / logo_rgb.size[0]))
            logo_resized = logo_rgb.resize((lw, lh), Image.LANCZOS)
            print(f"  Resized logo to: {lw}x{lh}")
            
            # Position bottom-right with padding
            pad = max(16, int(hw * 0.03))
            x = hw - logo_resized.size[0] - pad
            y = hh - logo_resized.size[1] - pad
            
            # Create semi-opaque white background
            overlay = Image.new('RGBA', h2_rgb.size, (255, 255, 255, 0))
            od = ImageDraw.Draw(overlay)
            margin = 12
            od.rectangle(
                [x - margin, y - margin, x + logo_resized.size[0] + margin, y + logo_resized.size[1] + margin],
                fill=(255, 255, 255, 210)
            )
            
            # Composite onto hero
            h2_rgba = h2_rgb.convert('RGBA')
            h2_rgba = Image.alpha_composite(h2_rgba, overlay)
            logo_rgba = logo_resized.convert('RGBA')
            h2_rgba.paste(logo_rgba, (x, y), logo_rgba)
            
            # Save merged @2x
            merged_2x = OUT / 'hero_merged@2x.webp'
            h2_rgba.convert('RGB').save(merged_2x, 'WEBP', quality=85, method=6)
            print(f"  Saved hero_merged@2x.webp ({h2_rgba.size[0]}x{h2_rgba.size[1]}, {merged_2x.stat().st_size/1024:.1f}KB)")
            
            # Create @1x by resizing @2x
            with Image.open(merged_2x) as m2:
                mw, mh = m2.size
                new_mw = max(320, mw // 2)
                new_mh = int(mh * (new_mw / mw))
                m1 = m2.resize((new_mw, new_mh), Image.LANCZOS)
                merged_1x = OUT / 'hero_merged@1x.webp'
                m1.convert('RGB').save(merged_1x, 'WEBP', quality=80, method=6)
                print(f"  Saved hero_merged@1x.webp ({new_mw}x{new_mh}, {merged_1x.stat().st_size/1024:.1f}KB)")
    except Exception as e:
        print(f"  ERROR compositing logo: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"  ERROR: Cannot composite (hero_src={hero_src}, logo exists={LOGO.exists()})")

print("\n" + "=" * 70)
print(f"COMPLETE: {variants_created} variants created, hero composited with logo")
print("=" * 70)

print(f"\nFinal image assets in {OUT}:")
webp_files = sorted(OUT.glob('*.webp'))
for f in webp_files:
    if 'stock' not in f.name:
        size = f.stat().st_size / 1024
        print(f"  {f.name:35} {size:8.1f} KB")
