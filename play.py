import os
from game import board
from pygame import *
#import psutil

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
    pieceSize = size//10
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

    def gameOver(self, side: bool, draw: bool = False):
        print("game over") #TODO
        if draw: print("Draw")
        elif side: print("white won")
        else: print("balck won") 

    # determine select and selcect move
    def select(self, side: bool = True):

        # mark king if it's in check
        if self.new.inCheck(True):
            x,y = self.new.chessPos(self.new.locateKing(True))
            if not side: x, y = 7-x, 7-y
            draw.rect(self.screen, self.red, (y*self.square, x*self.square, self.square, self.square), self.square//16)
        elif self.new.inCheck(False):
            x,y = self.new.chessPos(self.new.locateKing(False))
            if not side: x, y = 7-x, 7-y
            draw.rect(self.screen, self.red, (y*self.square, x*self.square, self.square, self.square), self.square//16)

        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()
        sx, sy = self.selected

        if mb[2]:
            self.isSelected = False
            self.selected = (-1,-1)

        elif mb[0]:

            if self.mbhold:
                mx = self.mxhold
                my = self.myhold

            if side: sx,sy = mx // self.square, my // self.square
            else: sx,sy = 7 - mx//self.square, 7 - my // self.square

            if (self.isSelected):
                for i in self.tempattack + self.tempresult:
                    if side: m = self.new.listPos(self.selected[1]//self.square,self.selected[0]//self.square)
                    else: m = self.new.listPos(7-self.selected[1]//self.square,7-self.selected[0]//self.square)
                    if (self.new.listPos(sy,sx) == i) and self.new.moveTest(m,i):
                        self.new.move(m,i)
                        self.turn = not self.turn
                    self.isSelected = False
                        
            if (self.turn and (self.new.colour(self.new.listPos(sy,sx)) == 1)) or (not self.turn and (self.new.colour(self.new.listPos(sy,sx)) == 2)):
                self.tempresult, self.tempattack = self.new.legal(self.new.listPos(sy,sx))
            else:
                self.tempresult, self.tempattack = [],[]

            if side: sx, sy = sx * self.square, sy * self.square
            else: sx, sy = (7 - sx) * self.square, (7 - sy)*self.square

            self.isSelected = True
            self.selected = sx, sy
            
        if (self.isSelected):
            draw.rect(self.screen, self.green, (sx, sy, self.square, self.square), self.square//16)
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
                draw.rect(self.screen, self.red, (tempy, tempx, self.square, self.square), self.square//16)

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

    def draw_board(self, side: bool = True):
        self.draw_base(side)
        b = self.new.state
        for i, r in enumerate(b):
            for j, p in enumerate(r):
                if side: row, col = i, j
                else: row, col = 7 - i, 7 - j
                match p:
                    case 'P':
                        self.screen.blit(self.chesspieces['pawn'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'R':
                        self.screen.blit(self.chesspieces['rook'],(col * self.square + self.cent,row * self.square + self.cent))
                    case 'B':
                        self.screen.blit(self.chesspieces['bishop'],(col * self.square + self.cent,row * self.square + self.cent))
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
        

def main():
    side = True
    g1 = play(side)
    run=True
    while run:
        for e in event.get():       
            if e.type == QUIT:      
                run=False
        g1.draw_board(side)
        g1.select(side)
        if g1.new.isDraw(side):
            g1.gameOver(side, True)
            run = False
        elif g1.new.isDraw(not side):
            g1.gameOver(not side, True)
        elif g1.new.isMate(side):
            g1.gameOver(side)
            run = False
        elif g1.new.isMate(not side):
            g1.gameOver(not side)
            run = False
        #print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        display.flip()
    quit()


if __name__ == "__main__":
    main()

