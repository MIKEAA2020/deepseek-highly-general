#!/usr/bin/env python3
"""Extract just the answer (after Thought for N seconds) from DeepSeek share."""
import json
import re
from pathlib import Path

raw = Path('/home/z/my-project/download/deepseek_share.json').read_text(encoding='utf-8', errors='ignore')
data = json.loads(raw)
html = data.get('data', {}).get('html', '')

# Strip everything
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<noscript[^>]*>.*?</noscript>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n\s*\n+', '\n\n', text)
text = re.sub(r'[ \t]+', ' ', text).strip()

# Find "Thought for X seconds" marker
m = re.search(r'(Thought for \d+ seconds)', text)
if m:
    # Find subsequent user-looking markers
    after = text[m.end():]
    # Look for next user input or end markers
    # In DeepSeek shares, conversation alternates user/assistant
    # Let's look for "shouldn't there be" type question patterns or end markers
    
    # Save just the answer part (after "Thought for N seconds") up to footer
    Path('/home/z/my-project/download/deepseek_answer.txt').write_text(after, encoding='utf-8')
    print(f"Answer length: {len(after)} chars")
    print("=" * 60)
    print(after[:6000])
    print("=" * 60)
    print("...")
    print("=" * 60)
    print(after[-2000:])
else:
    print("Thought marker not found")
    print(text[:3000])
