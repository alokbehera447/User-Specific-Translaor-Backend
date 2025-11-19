file_path = "/home/diracai-alok/Alok_work/User-Specific-Translaor_Backend/venv311/lib/python3.11/site-packages/f5_tts/infer/utils_infer.py"

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

print("Before fix:")
lines = content.split('\n')
for i, line in enumerate(lines[38:46], 39):
    print(f"{i}: {line}")

# Fix the specific problematic lines
# Line 42: if torch.xpu.is_available()
new_lines = []
for line in lines:
    if 'torch.xpu.is_available()' in line:
        line = line.replace('torch.xpu.is_available()', 'hasattr(torch, "xpu") and torch.xpu.is_available()')
    new_lines.append(line)

# Join back and write
fixed_content = '\n'.join(new_lines)
with open(file_path, 'w') as f:
    f.write(fixed_content)

print("\nAfter fix:")
lines = fixed_content.split('\n')
for i, line in enumerate(lines[38:46], 39):
    print(f"{i}: {line}")

print("✓ Fixed f5-tts XPU checks")
