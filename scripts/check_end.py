#!/usr/bin/env python3
"""Check the full page_reader response for any fields or content I missed."""
import json
from pathlib import Path

raw = Path('/home/z/my-project/download/deepseek_share.json').read_text(encoding='utf-8', errors='ignore')
print(f"JSON file size: {len(raw)} chars")

data = json.loads(raw)
print(f"\nTop-level keys: {list(data.keys())}")

if 'data' in data:
    d = data['data']
    print(f"\n'data' keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str):
                print(f"  {k}: {len(v)} chars (preview: {v[:200]!r})")
            else:
                print(f"  {k}: {type(v).__name__} = {v!r}" if not isinstance(v, (dict, list)) else f"  {k}: {type(v).__name__}")

# Look at the very end of the HTML to see if I missed anything
html = data.get('data', {}).get('html', '')
print(f"\n=== HTML total length: {len(html)} ===")
print(f"\n=== LAST 5000 chars of HTML ===")
print(html[-5000:])
