import os
from game import board
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
    new = board()
    size = 600
    square = size // 8
    pieceSize = size/10
    cent = (square - pieceSize)//2
    mbhold = False
    mxhold = -2
    myhold = -2

    #turn is True for white and False for black
    turn = True

    tempresult = []
    tempattack = []
    
    white,black,green,red = (230,196,146),(84,54,36),(0,153,76),(255,0,0)

    selected = (-1, -1)
    isSelected = False

    chesspieces = load_images('style/pixle')

    def __init__(self, side: bool = True, size: int = 600):
        self.size = (size // 8) * 8
        self.square = size//8
        self.pieceSize = size//10
        self.cent = (self.square - self.pieceSize)//2

        for pieces in self.chesspieces:
            self.chesspieces[pieces] = transform.scale(self.chesspieces[pieces], (self.pieceSize, self.pieceSize))

        self.screen = display.set_mode((size, size))

    # translate mouse position to cooridnates on the board, side = True means white, else black
    def translate(self, mx: int, my: int, side: bool = True) -> tuple[int, int]:
        if side:
            squarex = mx // self.square
            squarey = my // self.square
        else:
            squarex = (self.size - mx) // self.square
            squarey = (self.size - my) // self.square
        return squarex, squarey

    # determine select and selcect move
    def select(self, side: bool = True):
        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()
        sx, sy = self.selected

        if mb[2]:
            self.isSelected = False
            self.selected = (-1,-1)
            self.draw_board(side)
        elif mb[0]:

            if self.mbhold:
                mx = self.mxhold
                my = self.myhold

            if side: sx,sy = mx // self.square, my // self.square
            else: sx,sy = 7 - mx//self.square, 7 - my // self.square

            if (self.isSelected):
                for i in self.tempattack + self.tempresult:
                    if (self.new.listPos(sy,sx) == i):
                        if side: self.new.move(self.new.listPos(self.selected[1]//self.square,self.selected[0]//self.square),i)
                        else: self.new.move(self.new.listPos(7-self.selected[1]//self.square,7-self.selected[0]//self.square),i)
                        self.isSelected = False
                        self.turn = not self.turn
                        
            if (self.turn and (self.new.colour(self.new.listPos(sy,sx)) == 1)) or (not self.turn and (self.new.colour(self.new.listPos(sy,sx)) == 2)):
                self.tempresult, self.tempattack = self.new.legal(self.new.listPos(sy,sx))
            else:
                self.tempresult, self.tempattack = [],[]

            if side: sx, sy = sx * self.square, sy * self.square
            else: sx, sy = (7 - sx) * self.square, (7-sy)*self.square

            self.isSelected = True
            self.selected = sx, sy
            
        if (self.isSelected):
            draw.rect(self.screen, self.green, (sx, sy, self.square, self.square), self.size//100)
            for i in self.tempresult:
                tempx, tempy = self.new.chessPos(i)
                if side: tempx, tempy = tempx * self.square, tempy * self.square
                else: tempx, tempy = self.size - tempx * self.square - self.square, self.size - tempy * self.square - self.square
                draw.circle(self.screen, self.green, (tempy + self.square//2, tempx + self.square//2), self.square//7)
            for i in self.tempattack:
                tempx, tempy = self.new.chessPos(i)
                if side: tempx, tempy = tempx * self.square, tempy * self.square
                else: tempx, tempy = self.size - tempx * self.square - self.square, self.size - tempy * self.square - self.square
                # attackable unit
                draw.rect(self.screen, self.red, (tempy, tempx, self.square, self.square), self.size//100)

        # determine if the left click is long hold
        mb = mouse.get_pressed()
        if mb[0]:
            self.mbhold = True
            self.mxhold = mx
            self.myhold = my
        else:
            self.mbhold = False

    def draw_base(self, side: bool = True):
        for i in range(8):
            for j in range(9):
                if not side: i, j = i, j - 1
                if (i + j) % 2:
                    draw.rect(self.screen,self.black,(i*self.square,j*self.square,self.square, self.square))
                else:
                    draw.rect(self.screen,self.white,(i*self.square,j*self.square,self.square, self.square))

    #def lettertoword(self, letter: str):
        
        
    def draw_board(self, side: bool = True):
        self.draw_base(side)
        b = self.new.state
        for i, r in enumerate(self.new.state):
            for j, p in enumerate(r):
                if side: row, col = i, j
                else: row, col = 7 - i, 7 - j
                match p:
                    case 'P':
                        self.screen.blit(self.chesspieces['pawn'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'R':
                        self.screen.blit(self.chesspieces['rook'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'B':
                        self.screen.blit(self.chesspieces['pawn'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'Q':
                        self.screen.blit(self.chesspieces['queen'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'N':
                        self.screen.blit(self.chesspieces['knight'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'K':
                        self.screen.blit(self.chesspieces['king'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'p':
                        self.screen.blit(self.chesspieces['pawn1'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'r':
                        self.screen.blit(self.chesspieces['rook1'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'b':
                        self.screen.blit(self.chesspieces['bishop1'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'q':
                        self.screen.blit(self.chesspieces['queen1'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'n':
                        self.screen.blit(self.chesspieces['knight1'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'k':
                        self.screen.blit(self.chesspieces['king1'],(col * self.square + self.cent,row * self.square + self.cent))
        #draw.circle(self.screen, (255,0,0), (100,100), 80, 10)
                    

def main():
    side = False
    g1 = play(side)
    run=True
    while run:
        for e in event.get():       
            if e.type == QUIT:      
                run=False
        g1.draw_board(side)
        g1.select(side)
        display.flip()
    quit()


if __name__ == "__main__":
    main()

