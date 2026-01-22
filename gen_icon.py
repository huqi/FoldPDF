import os

icon_path = 'app_icon.ico'
if os.path.exists(icon_path):
    with open(icon_path, 'rb') as f:
        binary_data = f.read()
    
    # Generate as a simple Python file
    lines = []
    lines.append("# -*- coding: utf-8 -*-")
    lines.append('"""Icon binary data"""')
    lines.append("")
    lines.append("ICON_BINARY_DATA = bytes([")
    
    # Add binary data in chunks of 15 bytes per line
    for i in range(0, len(binary_data), 15):
        chunk = binary_data[i:i+15]
        hex_vals = ', '.join(f'0x{b:02x}' for b in chunk)
        lines.append(f"    {hex_vals},")
    
    # Remove trailing comma from last line
    lines[-1] = lines[-1].rstrip(',')
    lines.append("])")
    
    # Write file
    with open('icon_data.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated icon_data.py ({len(binary_data)} bytes)")
else:
    print(f"Error: {icon_path} not found")
