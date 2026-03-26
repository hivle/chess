#!/usr/bin/env python3
import os
from game import Board
from ai import best_move
from pygame import *


def load_images(path_to_directory):
    """Load piece images. Uses spritesheet.png if available, else individual files."""
    sheet_path = os.path.join(path_to_directory, 'spritesheet.png')
    if os.path.exists(sheet_path):
        return load_spritesheet(sheet_path)
    image_dict = {}
    for filename in os.listdir(path_to_directory):
        if filename.endswith('.png') and filename != 'spritesheet.png':
            path = os.path.join(path_to_directory, filename)
            key = filename[:-4]
            image_dict[key] = image.load(path)
    return image_dict


def load_spritesheet(path):
    """Load piece images from a sprite sheet.

    Layout: 6 columns (pawn, rook, knight, bishop, queen, king) x 2 rows (white, black)
    """
    sheet = image.load(path)
    sw, sh = sheet.get_size()
    tile_w, tile_h = sw // 6, sh // 2
    pieces_order = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
    images = {}
    for col, name in enumerate(pieces_order):
        white_rect = Rect(col * tile_w, 0, tile_w, tile_h)
        black_rect = Rect(col * tile_w, tile_h, tile_w, tile_h)
        images[name] = sheet.subsurface(white_rect).copy()
        images[name + '1'] = sheet.subsurface(black_rect).copy()
    return images


class play:
    white, black, green, red = (230,196,146),(84,54,36),(0,153,76),(255,0,0)

    def __init__(self, side: bool = True, size: int = 600, flip: bool = False, ai_depth: int = 0):
        init()
        self.new = Board()
        self.flip = flip
        self.m = True
        self.side = side
        self.ai_depth = ai_depth  # 0 = no AI, 1-4 = AI difficulty
        self.size = (size // 8) * 8
        self.square = size // 8
        self.pieceSize = size // 10
        self.cent = (self.square - self.pieceSize) // 2
        raw_images = load_images('style/pixle')
        for key in raw_images:
            raw_images[key] = transform.scale(raw_images[key], (self.pieceSize, self.pieceSize))
        # Map board characters to their images
        self.pieceImages = {
            'P': raw_images['pawn'],   'p': raw_images['pawn1'],
            'R': raw_images['rook'],   'r': raw_images['rook1'],
            'B': raw_images['bishop'], 'b': raw_images['bishop1'],
            'Q': raw_images['queen'],  'q': raw_images['queen1'],
            'N': raw_images['knight'], 'n': raw_images['knight1'],
            'K': raw_images['king'],   'k': raw_images['king1'],
        }
        self.text = font.Font('Fonts/ka1.ttf', self.square // 2)
        self.screen = display.set_mode((size, size))
        self.gameOverText = None

        # Selection state
        self.isSelected = False
        self.selected = (-1, -1)  # pixel coords of selected square
        self.selectedSquare = ''  # chess notation of selected piece
        self.tempresult = []
        self.tempattack = []
        self.mbhold = False

    @property
    def whiteTurn(self):
        """Single source of truth for whose turn it is."""
        return self.new.state["whiteTurn"]

    def gameOver(self, whiteWin: bool, isDraw: bool = False):
        if isDraw:
            self.gameOverText = "Draw!"
        elif whiteWin:
            self.gameOverText = "White Wins!"
        else:
            self.gameOverText = "Black Wins!"

    def drawGameOver(self):
        if self.gameOverText is None:
            return
        overlay = Surface((self.size, self.size), SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        text_surface = self.text.render(self.gameOverText, True, (255, 255, 255))
        tx = (self.size - text_surface.get_width()) // 2
        ty = (self.size - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (tx, ty))

    def _viewSide(self, side: bool) -> bool:
        """Return the effective view side accounting for flip mode."""
        if self.flip:
            return self.whiteTurn if side else not self.whiteTurn
        return side

    def markCheck(self, side: bool = True):
        vs = self._viewSide(side)
        for isWhite in (True, False):
            if self.new.inCheck(isWhite):
                x, y = self.new.listPos(self.new.locateKing(isWhite))
                if not vs:
                    x, y = 7 - x, 7 - y
                draw.rect(self.screen, self.red, (y * self.square, x * self.square, self.square, self.square), self.square // 16)

    def _menu_button(self, label, x, y, mx, my, clicked):
        """Draw a menu button, return True if clicked."""
        normal = self.text.render(label, True, (255, 255, 255))
        hover = self.text.render(label, True, (230, 230, 230))
        rect = Rect(x, y, normal.get_width() + 10, normal.get_height())
        is_hover = rect.collidepoint(mx, my)
        self.screen.blit(hover if is_hover else normal, (x, y))
        return is_hover and clicked

    def menu(self):
        draw.rect(self.screen, self.white, (0, 0, self.size, self.size))
        title = self.text.render("Chess", True, (84, 54, 36))
        self.screen.blit(title, ((self.size - title.get_width()) // 2, self.size // 4))

        mx, my = mouse.get_pos()
        clicked = mouse.get_pressed()[0] and not self.mbhold

        x = self.size // 2 - self.square
        y0 = self.size // 2 - self.square // 2
        gap = self.square * 3 // 4

        options = [
            ("2 Player", 0),
            ("AI Easy", 1),
            ("AI Medium", 2),
            ("AI Hard", 3),
            ("Quit", -1),
        ]
        for i, (label, depth) in enumerate(options):
            if self._menu_button(label, x, y0 + i * gap, mx, my, clicked):
                if depth == -1:
                    quit()
                else:
                    self.ai_depth = depth
                    self.m = False
                    self.mbhold = True

        self.mbhold = mouse.get_pressed()[0]

    def _clearSelection(self):
        self.isSelected = False
        self.selected = (-1, -1)
        self.selectedSquare = ''
        self.tempresult = []
        self.tempattack = []

    def _isCurrentPlayerPiece(self, square: str) -> bool:
        clr = self.new.colour(square)
        return (self.whiteTurn and clr == 1) or (not self.whiteTurn and clr == 2)

    def _squarePixel(self, sq, vs):
        """Convert chess square to pixel (x, y) for drawing."""
        r, c = self.new.listPos(sq)
        if vs:
            return c * self.square, r * self.square
        return self.size - c * self.square - self.square, self.size - r * self.square - self.square

    def _clickedSquare(self, vs):
        """Get the chess square under the mouse cursor."""
        mx, my = mouse.get_pos()
        pc, pr = mx // self.square, my // self.square
        if not vs:
            pc, pr = 7 - pc, 7 - pr
        return self.new.chessPos(pr, pc), (mx // self.square * self.square, my // self.square * self.square)

    def select(self, side: bool = True):
        vs = self._viewSide(side)
        mb = mouse.get_pressed()

        if self.isSelected and not self._isCurrentPlayerPiece(self.selectedSquare):
            self._clearSelection()

        if mb[0] and not self.mbhold:
            sq, pixel = self._clickedSquare(vs)

            # Try to move selected piece to clicked square
            if self.isSelected and sq in self.tempresult + self.tempattack:
                if self.new.move(self.selectedSquare, sq):
                    self._clearSelection()
                    self.mbhold = True
                    return

            # Select a new piece or clear
            if self._isCurrentPlayerPiece(sq):
                self.tempresult, self.tempattack = self.new.legalFiltered(sq)
                self.isSelected = True
                self.selectedSquare = sq
                self.selected = pixel
            else:
                self._clearSelection()

        # Draw highlights
        if self.isSelected:
            draw.rect(self.screen, self.green, (*self.selected, self.square, self.square), self.square // 16)
            for sq in self.tempresult:
                px, py = self._squarePixel(sq, vs)
                draw.circle(self.screen, self.green, (px + self.square // 2, py + self.square // 2), self.square // 7)
            for sq in self.tempattack:
                px, py = self._squarePixel(sq, vs)
                draw.rect(self.screen, self.red, (px, py, self.square, self.square), self.square // 16)

        self.mbhold = mb[0]

    def draw_base(self):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2:
                    draw.rect(self.screen, self.black, (i * self.square, j * self.square, self.square, self.square))
                else:
                    draw.rect(self.screen, self.white, (i * self.square, j * self.square, self.square, self.square))

    def draw_board(self, side: bool = True):
        self.draw_base()
        vs = self._viewSide(side)
        for i, row in enumerate(self.new.board):
            for j, piece in enumerate(row):
                if piece in self.pieceImages:
                    r, c = (i, j) if vs else (7 - i, 7 - j)
                    self.screen.blit(self.pieceImages[piece], (c * self.square + self.cent, r * self.square + self.cent))


def main():
    side = True
    g1 = play(side, flip=False, ai_depth=0)  # menu sets ai_depth
    run = True
    gameEnded = False
    while run:
        for e in event.get():
            if e.type == QUIT:
                run = False
            elif e.type == KEYDOWN and e.key == K_LEFT:
                if not gameEnded and g1.new.back():
                    # back() restores whiteTurn from history - no manual flip needed
                    g1._clearSelection()
                    g1.mbhold = True  # consume any held click
            elif e.type == KEYDOWN and e.key == K_q:
                g1.m = True
                gameEnded = False
                g1.gameOverText = None
                g1.new = Board()  # new Board() resets whiteTurn to True
                g1._clearSelection()
                g1.mbhold = True  # consume any held click
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 3:
                    g1._clearSelection()

        if g1.m:
            g1.menu()
        else:
            g1.draw_board(side)
            g1.markCheck(side)
            if not gameEnded:
                # AI move: if it's the AI's turn (AI plays black when side=True)
                ai_is_turn = g1.ai_depth > 0 and g1.whiteTurn != side
                if ai_is_turn:
                    move = best_move(g1.new, g1.ai_depth)
                    if move:
                        g1.new.move(move[0], move[1])
                        g1._clearSelection()
                else:
                    g1.select(side)

            # Check game-over conditions based on whose turn it is
            if not gameEnded:
                if g1.new.isDraw(g1.whiteTurn):
                    g1.gameOver(False, isDraw=True)
                    gameEnded = True
                elif g1.new.isMate(g1.whiteTurn):
                    g1.gameOver(whiteWin=not g1.whiteTurn)
                    gameEnded = True

            if gameEnded:
                g1.drawGameOver()

        display.flip()
    quit()


if __name__ == "__main__":
    main()
