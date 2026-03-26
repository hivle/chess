import os
from game import Board
from pygame import *


def load_images(path_to_directory):
    image_dict = {}
    for filename in os.listdir(path_to_directory):
        if filename.endswith('.png'):
            path = os.path.join(path_to_directory, filename)
            key = filename[:-4]
            image_dict[key] = image.load(path)
    return image_dict


class play:
    white, black, green, red = (230,196,146),(84,54,36),(0,153,76),(255,0,0)

    def __init__(self, side: bool = True, size: int = 600, flip: bool = False):
        init()
        self.new = Board()
        self.flip = flip
        self.m = True
        self.side = side
        self.turn = True
        self.size = (size // 8) * 8
        self.square = size // 8
        self.pieceSize = size // 10
        self.cent = (self.square - self.pieceSize) // 2
        self.chesspieces = load_images('style/pixle')
        for pieces in self.chesspieces:
            self.chesspieces[pieces] = transform.scale(self.chesspieces[pieces], (self.pieceSize, self.pieceSize))
        self.text = font.Font('Fonts/ka1.ttf', self.square // 2)
        self.screen = display.set_mode((size, size))
        self.gameOverText = None

        # Selection state
        self.isSelected = False
        self.selected = (-1, -1)  # pixel coords of selected square
        self.tempresult = []
        self.tempattack = []
        self.mbhold = False
        self.mxhold = -2
        self.myhold = -2

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
            return self.turn if side else not self.turn
        return side

    def markCheck(self, side: bool = True):
        vs = self._viewSide(side)
        # Check both sides for check
        for isWhite in (True, False):
            if self.new.inCheck(isWhite):
                x, y = self.new.listPos(self.new.locateKing(isWhite))
                if not vs:
                    x, y = 7 - x, 7 - y
                draw.rect(self.screen, self.red, (y * self.square, x * self.square, self.square, self.square), self.square // 16)

    def menu(self):
        draw.rect(self.screen, self.white, (0, 0, self.size, self.size))
        play_text = self.text.render("Play", True, (255, 255, 255))
        playGrey = self.text.render("Play", True, (230, 230, 230))
        q = self.text.render("Quit", True, (255, 255, 255))
        qGrey = self.text.render("Quit", True, (230, 230, 230))
        play_x = self.size // 2 - self.square
        play_y = self.size // 2
        quit_x = self.size // 2 - self.square + self.pieceSize // 10
        quit_y = self.size // 2 + self.pieceSize
        clickb = Rect(play_x, play_y + self.square // 20, self.square * 5 // 3, self.square // 2)
        clickq = Rect(quit_x, quit_y, self.square * 5 // 3, self.square // 2)
        self.screen.blit(play_text, (play_x, play_y))
        self.screen.blit(q, (quit_x, quit_y))

        mx, my = mouse.get_pos()
        mb = mouse.get_pressed()
        if clickb.collidepoint(mx, my):
            self.screen.blit(playGrey, (play_x, play_y))
            if mb[0] == 1:
                self.m = False
        if clickq.collidepoint(mx, my):
            self.screen.blit(qGrey, (quit_x, quit_y))
            if mb[0] == 1:
                quit()

    def select(self, side: bool = True):
        vs = self._viewSide(side)
        mx, my = mouse.get_pos()
        mb = mouse.get_pressed()

        if mb[0]:
            # On held click, use original click position
            if self.mbhold:
                mx = self.mxhold
                my = self.myhold

            # Convert pixel to board col/row
            pixel_col, pixel_row = mx // self.square, my // self.square
            # Board coordinates (accounting for flipped view)
            if vs:
                board_col, board_row = pixel_col, pixel_row
            else:
                board_col, board_row = 7 - pixel_col, 7 - pixel_row

            clicked_square = self.new.chessPos(board_row, board_col)

            # If we already have a piece selected, try to move to clicked square
            if self.isSelected:
                if clicked_square in self.tempresult + self.tempattack:
                    # Compute the start square from the stored selection
                    sel_px, sel_py = self.selected
                    if vs:
                        start_col, start_row = sel_px // self.square, sel_py // self.square
                    else:
                        start_col, start_row = 7 - sel_px // self.square, 7 - sel_py // self.square
                    start_square = self.new.chessPos(start_row, start_col)
                    if self.new.move(start_square, clicked_square):
                        self.turn = not self.turn
                        self.isSelected = False
                        self.selected = (-1, -1)
                        self.tempresult, self.tempattack = [], []
                        # Update hold state and return early
                        self.mbhold = True
                        self.mxhold = mx
                        self.myhold = my
                        return

            # Select a new piece if it belongs to the current player
            clicked_colour = self.new.colour(clicked_square)
            if (self.turn and clicked_colour == 1) or (not self.turn and clicked_colour == 2):
                self.tempresult, self.tempattack = self.new.legalFiltered(clicked_square)
                self.isSelected = True
                self.selected = (pixel_col * self.square, pixel_row * self.square)
            else:
                self.tempresult, self.tempattack = [], []
                self.isSelected = False
                self.selected = (-1, -1)

        # Draw selection highlights
        if self.isSelected:
            sx, sy = self.selected
            draw.rect(self.screen, self.green, (sx, sy, self.square, self.square), self.square // 16)
            for sq in self.tempresult:
                tempx, tempy = self.new.listPos(sq)
                if vs:
                    px, py = tempy * self.square, tempx * self.square
                else:
                    px, py = self.size - tempy * self.square - self.square, self.size - tempx * self.square - self.square
                draw.circle(self.screen, self.green, (px + self.square // 2, py + self.square // 2), self.square // 7)
            for sq in self.tempattack:
                tempx, tempy = self.new.listPos(sq)
                if vs:
                    px, py = tempy * self.square, tempx * self.square
                else:
                    px, py = self.size - tempy * self.square - self.square, self.size - tempx * self.square - self.square
                draw.rect(self.screen, self.red, (px, py, self.square, self.square), self.square // 16)

        # Track mouse hold state
        mb = mouse.get_pressed()
        if mb[0]:
            self.mbhold = True
            self.mxhold = mx
            self.myhold = my
        else:
            self.mbhold = False

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
        b = self.new.board
        for i, r in enumerate(b):
            for j, p in enumerate(r):
                if vs:
                    row, col = i, j
                else:
                    row, col = 7 - i, 7 - j
                match p:
                    case 'P':
                        self.screen.blit(self.chesspieces['pawn'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'R':
                        self.screen.blit(self.chesspieces['rook'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'B':
                        self.screen.blit(self.chesspieces['bishop'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'Q':
                        self.screen.blit(self.chesspieces['queen'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'N':
                        self.screen.blit(self.chesspieces['knight'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'K':
                        self.screen.blit(self.chesspieces['king'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'p':
                        self.screen.blit(self.chesspieces['pawn1'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'r':
                        self.screen.blit(self.chesspieces['rook1'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'b':
                        self.screen.blit(self.chesspieces['bishop1'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'q':
                        self.screen.blit(self.chesspieces['queen1'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'n':
                        self.screen.blit(self.chesspieces['knight1'], (col * self.square + self.cent, row * self.square + self.cent))
                    case 'k':
                        self.screen.blit(self.chesspieces['king1'], (col * self.square + self.cent, row * self.square + self.cent))


def main():
    side = True
    g1 = play(side, flip=False)
    run = True
    gameEnded = False
    while run:
        for e in event.get():
            if e.type == QUIT:
                run = False
            elif e.type == KEYDOWN and e.key == K_LEFT:
                if not gameEnded and g1.new.back():
                    g1.turn = not g1.turn
                    g1.isSelected = False
                    g1.selected = (-1, -1)
                    g1.tempresult, g1.tempattack = [], []
            elif e.type == KEYDOWN and e.key == K_q:
                g1.m = True
                gameEnded = False
                g1.gameOverText = None
                g1.new = Board()
                g1.turn = True
                g1.isSelected = False
                g1.tempresult, g1.tempattack = [], []
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 3:
                    g1.isSelected = False
                    g1.selected = (-1, -1)
                    g1.tempresult, g1.tempattack = [], []

        if g1.m:
            g1.menu()
        else:
            g1.draw_board(side)
            g1.markCheck(side)
            if not gameEnded:
                g1.select(side)

            # Check game-over conditions based on whose turn it is
            if not gameEnded:
                if g1.new.isDraw(g1.turn):
                    g1.gameOver(False, isDraw=True)
                    gameEnded = True
                elif g1.new.isMate(g1.turn):
                    # Current player is mated, so the other player wins
                    g1.gameOver(whiteWin=not g1.turn)
                    gameEnded = True

            if gameEnded:
                g1.drawGameOver()

        display.flip()
    quit()


if __name__ == "__main__":
    main()
