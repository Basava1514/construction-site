#!/usr/bin/env python3
"""
Download stock images from Pexels, convert to WebP with @1x/@2x variants,
composite logo onto hero image, and save results.
"""
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from PIL import Image, ImageDraw
import json

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / 'docs' / 'static' / 'images' / 'stock_raw'
OUT = BASE / 'docs' / 'static' / 'images'
LOGO = OUT / 'logo.webp'

RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# Use Pexels API (high-quality free stock images, reliable)
# These are curated URLs for construction/industrial themes
pexels_urls = [
    'https://images.pexels.com/photos/3962672/pexels-photo-3962672.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # construction site
    'https://images.pexels.com/photos/3962666/pexels-photo-3962666.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # steel structure
    'https://images.pexels.com/photos/3938020/pexels-photo-3938020.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # welding
    'https://images.pexels.com/photos/3961954/pexels-photo-3961954.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # warehouse
    'https://images.pexels.com/photos/3962669/pexels-photo-3962669.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # factory
    'https://images.pexels.com/photos/2146177/pexels-photo-2146177.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop',  # residential
]

def download_image(url, dest, attempt=0, max_attempts=5):
    """Download image with retries."""
    if attempt >= max_attempts:
        print(f"  Failed to download after {max_attempts} attempts")
        return False
    try:
        print(f"  Attempt {attempt+1}: downloading...")
        req = urlopen(url, timeout=30)
        data = req.read()
        req.close()
        if len(data) < 5000:
            print(f"    Response too small ({len(data)} bytes), retrying...")
            time.sleep(2 * (attempt + 1))
            return download_image(url, dest, attempt + 1, max_attempts)
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"  Downloaded {len(data)} bytes -> {dest.name}")
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        time.sleep(2 * (attempt + 1))
        return download_image(url, dest, attempt + 1, max_attempts)

def to_rgb(im):
    """Convert image to RGB, handling transparency."""
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        if im.mode == 'P':
            im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
        return bg
    return im.convert('RGB')

# Step 1: Download images
print("=" * 70)
print("STEP 1: Downloading high-quality images from Pexels")
print("=" * 70)
downloaded = []
for i, url in enumerate(pexels_urls, start=1):
    dest = RAW / f'stock_{i}.jpg'
    if dest.exists():
        print(f"Stock {i} already exists; skipping download")
        downloaded.append(dest)
        continue
    if download_image(url, dest):
        downloaded.append(dest)
    else:
        print(f"Stock {i} download failed; will skip processing")

if not downloaded:
    print("\nERROR: No images downloaded. Exiting.")
    sys.exit(1)

# Step 2: Convert and create variants
print("\n" + "=" * 70)
print("STEP 2: Converting to WebP and creating @1x/@2x variants")
print("=" * 70)
hero_2x_path = None
for src in downloaded:
    i = int(src.stem.split('_')[1])
    try:
        print(f"Processing stock_{i}...")
        with Image.open(src) as im:
            im_rgb = to_rgb(im)
            w, h = im_rgb.size
            
            # Save @2x (original size as WebP)
            out2 = OUT / f'stock_{i}@2x.webp'
            im_rgb.save(out2, 'WEBP', quality=85, method=6)
            print(f"  Saved stock_{i}@2x.webp ({w}x{h}, {out2.stat().st_size/1024:.1f}KB)")
            if i == 1:
                hero_2x_path = out2
            
            # Save @1x (half width, min 320px)
            new_w = max(320, w // 2)
            new_h = int(h * (new_w / w))
            im1 = im_rgb.resize((new_w, new_h), Image.LANCZOS)
            out1 = OUT / f'stock_{i}@1x.webp'
            im1.save(out1, 'WEBP', quality=80, method=6)
            print(f"  Saved stock_{i}@1x.webp ({new_w}x{new_h}, {out1.stat().st_size/1024:.1f}KB)")
    except Exception as e:
        print(f"  ERROR processing {src}: {e}")
        import traceback
        traceback.print_exc()

# Step 3: Composite logo onto hero image
print("\n" + "=" * 70)
print("STEP 3: Compositing company logo onto hero image")
print("=" * 70)
if hero_2x_path and hero_2x_path.exists() and LOGO.exists():
    try:
        print(f"Hero image: {hero_2x_path.name}")
        print(f"Logo image: {LOGO.name}")
        with Image.open(hero_2x_path) as h2, Image.open(LOGO) as logo:
            h2_rgb = to_rgb(h2)
            logo_rgb = to_rgb(logo)
            
            hw, hh = h2_rgb.size
            print(f"Hero dimensions: {hw}x{hh}")
            print(f"Logo dimensions: {logo_rgb.size}")
            
            # Scale logo to 15-20% of hero width
            lw = max(80, min(300, int(hw * 0.18)))
            lh = int(logo_rgb.size[1] * (lw / logo_rgb.size[0]))
            logo_resized = logo_rgb.resize((lw, lh), Image.LANCZOS)
            print(f"Resized logo to: {lw}x{lh}")
            
            # Position bottom-right with padding
            pad = max(12, int(hw * 0.02))
            x = hw - logo_resized.size[0] - pad
            y = hh - logo_resized.size[1] - pad
            
            # Create overlay with rounded background
            overlay = Image.new('RGBA', h2_rgb.size, (255, 255, 255, 0))
            od = ImageDraw.Draw(overlay)
            margin = 8
            od.rectangle(
                [x - margin, y - margin, x + logo_resized.size[0] + margin, y + logo_resized.size[1] + margin],
                fill=(255, 255, 255, 220)
            )
            
            # Composite onto hero
            h2_rgba = h2_rgb.convert('RGBA')
            h2_rgba = Image.alpha_composite(h2_rgba, overlay)
            logo_rgba = logo_resized.convert('RGBA')
            h2_rgba.paste(logo_rgba, (x, y), logo_rgba)
            
            # Save merged @2x
            merged_2x = OUT / 'hero_merged@2x.webp'
            h2_rgba.convert('RGB').save(merged_2x, 'WEBP', quality=85, method=6)
            print(f"Saved hero_merged@2x.webp ({h2_rgba.size[0]}x{h2_rgba.size[1]}, {merged_2x.stat().st_size/1024:.1f}KB)")
            
            # Create @1x by resizing @2x
            with Image.open(merged_2x) as m2:
                mw, mh = m2.size
                new_mw = max(320, mw // 2)
                new_mh = int(mh * (new_mw / mw))
                m1 = m2.resize((new_mw, new_mh), Image.LANCZOS)
                merged_1x = OUT / 'hero_merged@1x.webp'
                m1.convert('RGB').save(merged_1x, 'WEBP', quality=80, method=6)
                print(f"Saved hero_merged@1x.webp ({new_mw}x{new_mh}, {merged_1x.stat().st_size/1024:.1f}KB)")
    except Exception as e:
        print(f"ERROR compositing logo: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Cannot composite:")
    if not hero_2x_path:
        print(f"  - hero_2x_path not set")
    elif not hero_2x_path.exists():
        print(f"  - hero image not found: {hero_2x_path}")
    if not LOGO.exists():
        print(f"  - logo not found: {LOGO}")

print("\n" + "=" * 70)
print("COMPLETE: Stock images processed and ready for use")
print("=" * 70)
print(f"\nGenerated files in {OUT}:")
for f in sorted(OUT.glob('stock_*@*.webp')) + sorted(OUT.glob('hero_merged@*.webp')):
    size = f.stat().st_size / 1024
    print(f"  {f.name:30} {size:8.1f} KB")
