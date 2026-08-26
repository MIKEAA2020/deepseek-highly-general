#!/usr/bin/env python3
"""Extract full readable DeepSeek conversation."""
import json
import re
from pathlib import Path

raw = Path('/home/z/my-project/download/deepseek_share.json').read_text(encoding='utf-8', errors='ignore')
data = json.loads(raw)
html = data.get('data', {}).get('html', '')

# Try to find og:description content (often holds full DeepSeek answer)
og_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
if og_match:
    og = og_match.group(1)
    # Unescape HTML entities
    og = og.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    Path('/home/z/my-project/download/deepseek_og.txt').write_text(og, encoding='utf-8')
    print(f"=== OG description length: {len(og)} ===")
    print(og[:5000])
    print("...")
    print(og[-2000:])

print("\n\n--- SEPARATOR ---\n\n")

# Strip all scripts/styles/tags to get visible text
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<noscript[^>]*>.*?</noscript>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n\s*\n', '\n\n', text)
text = re.sub(r'[ \t]+', ' ', text).strip()

Path('/home/z/my-project/download/deepseek_text.txt').write_text(text, encoding='utf-8')
print(f"=== Stripped text length: {len(text)} ===")
print(text[:8000])
