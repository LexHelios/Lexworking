#!/usr/bin/env python3
"""
Create a test image for multimodal testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image
width, height = 800, 600
image = Image.new('RGB', (width, height), color='#1a1a2e')
draw = ImageDraw.Draw(image)

# Draw some shapes and text
# Gradient background effect
for i in range(height):
    color_value = int(26 + (40 - 26) * (i / height))
    draw.line([(0, i), (width, i)], fill=(color_value, color_value, color_value + 20))

# Add cyberpunk-style elements
draw.rectangle([50, 50, 750, 100], fill='#00d9ff', outline='#0080ff', width=3)
draw.text((100, 60), "LEX MULTIMODAL TEST", fill='#000000', font=None)

# Add some geometric shapes
draw.polygon([(200, 200), (300, 150), (400, 200), (350, 300), (250, 300)], 
             fill='#ff006e', outline='#ff0090', width=2)

draw.ellipse([450, 200, 600, 350], fill='#00d9ff', outline='#00a0ff', width=3)

# Add tech grid lines
for x in range(0, width, 50):
    draw.line([(x, 0), (x, height)], fill='#333355', width=1)
for y in range(0, height, 50):
    draw.line([(0, y), (width, y)], fill='#333355', width=1)

# Add description text
draw.text((50, 450), "This is a test image with cyberpunk aesthetic", fill='#00d9ff')
draw.text((50, 480), "Contains: shapes, colors, text, and grid pattern", fill='#ff006e')
draw.text((50, 510), "Purpose: Testing LEX multimodal vision capabilities", fill='#00ff88')

# Save the image
test_image_path = "test_cyberpunk.jpg"
image.save(test_image_path, quality=95)
print(f"Created test image: {test_image_path}")