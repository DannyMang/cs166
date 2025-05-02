from cairosvg import svg2png
import os

# Read the SVG file
with open('icons/icon.svg', 'r') as f:
    svg_content = f.read()

# Generate different sizes
sizes = [16, 48, 128]
for size in sizes:
    output_file = f'icons/icon{size}.png'
    svg2png(bytestring=svg_content.encode('utf-8'),
            write_to=output_file,
            output_width=size,
            output_height=size)
    print(f"Generated {output_file}") 