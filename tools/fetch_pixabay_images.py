#!/usr/bin/env python3
"""
Use Pixabay free images to download contextually relevant images for services and projects.
Creates WebP variants for optimal web delivery.
"""
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from PIL import Image
import json

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / 'docs' / 'static' / 'images' / 'pixabay_raw'
OUT = BASE / 'docs' / 'static' / 'images'

RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# Pixabay direct URLs (high-quality, CC0 license, no API key needed for these curated links)
service_images = {
    'steel-fabrication': 'https://cdn.pixabay.com/photo/2016/11/18/16/19/crane-1836512_1280.jpg',  # Steel beams
    'structural-fabrication': 'https://cdn.pixabay.com/photo/2018/02/08/17/03/steel-construction-3139100_1280.jpg',  # Structural steel
    'ms-fabrication': 'https://cdn.pixabay.com/photo/2019/07/01/11/41/metallurgy-4307614_1280.jpg',  # Metal work
    'industrial-shed': 'https://cdn.pixabay.com/photo/2018/04/12/08/36/warehouse-3314304_1280.jpg',  # Industrial warehouse
    'commercial-building': 'https://cdn.pixabay.com/photo/2016/11/19/19/05/office-building-1840846_1280.jpg',  # Modern building
    'residential-construction': 'https://cdn.pixabay.com/photo/2015/10/20/17/14/house-998265_1280.jpg',  # House construction
}

project_images = {
    'industrial-warehouse': 'https://cdn.pixabay.com/photo/2016/03/27/19/43/industrial-1283604_1280.jpg',  # Industrial facility
    'factory-shed': 'https://cdn.pixabay.com/photo/2019/12/19/10/44/factory-4705283_1280.jpg',  # Factory building
    'steel-structure': 'https://cdn.pixabay.com/photo/2017/10/09/09/37/architecture-2834302_1280.jpg',  # Steel construction
    'commercial-complex': 'https://cdn.pixabay.com/photo/2016/11/18/16/19/building-1836502_1280.jpg',  # Commercial complex
    'residential-villa': 'https://cdn.pixabay.com/photo/2016/08/11/01/32/luxury-1583174_1280.jpg',  # Modern villa
    'industrial-plant': 'https://cdn.pixabay.com/photo/2019/11/09/20/02/industrial-4612325_1280.jpg',  # Industrial plant
}

def download_image(url, dest, attempt=0, max_attempts=3):
    """Download image with retries."""
    if attempt >= max_attempts:
        print(f"  [FAIL] Failed after {max_attempts} attempts")
        return False
    try:
        print(f"  [DOWNLOADING] Attempt {attempt+1}...")
        req = urlopen(url, timeout=30)
        data = req.read()
        req.close()
        if len(data) < 5000:
            print(f"    Response too small ({len(data)} bytes), retrying...")
            time.sleep(2)
            return download_image(url, dest, attempt + 1, max_attempts)
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"  [OK] Downloaded {len(data)/1024:.1f}KB -> {dest.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}; retry...")
        time.sleep(2)
        return download_image(url, dest, attempt + 1, max_attempts)

def to_rgb(im):
    """Convert to RGB."""
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        if im.mode == 'P':
            im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
        return bg
    return im.convert('RGB')

print("="*70)
print("STEP 1: Downloading service images from Pixabay (CC0 license)")
print("="*70)
service_files = {}
for name, url in service_images.items():
    dest = RAW / f'{name}.jpg'
    if dest.exists():
        print(f"[OK] {name} exists; skipping")
        service_files[name] = dest
        continue
    if download_image(url, dest):
        service_files[name] = dest

print("\n" + "="*70)
print("STEP 2: Downloading project images from Pixabay (CC0 license)")
print("="*70)
project_files = {}
for name, url in project_images.items():
    dest = RAW / f'{name}.jpg'
    if dest.exists():
        print(f"[OK] {name} exists; skipping")
        project_files[name] = dest
        continue
    if download_image(url, dest):
        project_files[name] = dest

print("\n" + "="*70)
print("STEP 3: Converting to WebP with @1x/@2x variants")
print("="*70)

all_files = {**service_files, **project_files}
if not all_files:
    print("ERROR: No images downloaded")
    sys.exit(1)

for name, src in all_files.items():
    try:
        with Image.open(src) as im:
            im_rgb = to_rgb(im)
            w, h = im_rgb.size
            
            # Save @2x
            out2 = OUT / f'{name}@2x.webp'
            im_rgb.save(out2, 'WEBP', quality=85, method=6)
            print(f"[OK] {name}@2x.webp ({w}x{h}, {out2.stat().st_size/1024:.1f}KB)")
            
            # Save @1x
            new_w = max(320, w // 2)
            new_h = int(h * (new_w / w))
            im1 = im_rgb.resize((new_w, new_h), Image.LANCZOS)
            out1 = OUT / f'{name}@1x.webp'
            im1.save(out1, 'WEBP', quality=80, method=6)
            print(f"[OK] {name}@1x.webp ({new_w}x{new_h}, {out1.stat().st_size/1024:.1f}KB)")
    except Exception as e:
        print(f"[ERROR] Processing {name}: {e}")

print("\n" + "="*70)
print("COMPLETE: Images downloaded and converted to WebP")
print("="*70)
