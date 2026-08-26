#!/usr/bin/env python3
"""Extract conversation content from DeepSeek share JSON."""
import json
import re
from pathlib import Path

src = Path('/home/z/my-project/download/deepseek_share.json')
raw = src.read_text(encoding='utf-8', errors='ignore')
print(f"Total length: {len(raw)} chars")

try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    # try to extract just the html field
    data = None

if data:
    html = data.get('data', {}).get('html', '')
    desc = data.get('data', {}).get('description', '')
    title = data.get('data', {}).get('title', '')
    print(f"Title: {title}")
    print(f"Description (first 1500 chars): {desc[:1500]}")
    print(f"HTML length: {len(html)}")
    
    # Look for og:description meta content which often holds the first message
    og_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
    if og_match:
        print(f"\n=== OG Description ===\n{og_match.group(1)[:2000]}")
    
    # Look for embedded JSON blobs in the HTML (Next.js __NEXT_DATA__ etc.)
    next_data = re.search(r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>', html)
    if next_data:
        print(f"\n=== __NEXT_DATA__ found (length {len(next_data.group(1))}) ===")
        print(next_data.group(1)[:1500])
    
    # Look for window.__NEXT_DATA__
    next_data2 = re.search(r'window\.__NEXT_DATA__\s*=\s*(\{.*?\});', html, re.DOTALL)
    if next_data2:
        print(f"\n=== window.__NEXT_DATA__ found (length {len(next_data2.group(1))}) ===")
        print(next_data2.group(1)[:1500])
    
    # Save raw html for inspection
    Path('/home/z/my-project/download/deepseek_raw.html').write_text(html, encoding='utf-8')
    print("\nRaw HTML saved to deepseek_raw.html")
    
    # Strip all tags - try to find readable text content
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"\n=== Stripped text (first 3000 chars) ===\n{text[:3000]}")
    print(f"\nTotal stripped text length: {len(text)}")
