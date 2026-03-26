#!/usr/bin/env python3
"""Combine individual piece PNGs into a single sprite sheet.

Layout: 6 columns (pawn, rook, knight, bishop, queen, king) x 2 rows (white, black)
Run once to generate style/pixle/spritesheet.png
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from pygame import image, Surface, SRCALPHA, init

init()

PIECES_ORDER = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
SRC_DIR = 'style/pixle'

# Load first image to get dimensions
sample = image.load(os.path.join(SRC_DIR, 'pawn.png'))
w, h = sample.get_size()

# Create sprite sheet: 6 columns x 2 rows
sheet = Surface((w * 6, h * 2), SRCALPHA)

for col, name in enumerate(PIECES_ORDER):
    white_img = image.load(os.path.join(SRC_DIR, f'{name}.png'))
    black_img = image.load(os.path.join(SRC_DIR, f'{name}1.png'))
    sheet.blit(white_img, (col * w, 0))
    sheet.blit(black_img, (col * w, h))

output = os.path.join(SRC_DIR, 'spritesheet.png')
image.save(sheet, output)
print(f"Saved {output} ({w*6}x{h*2}, tile size {w}x{h})")
