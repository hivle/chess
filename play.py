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
    mbhold = False
    mxhold = -2
    myhold = -2

    #turn is True for white and False for black

    tempresult = []
    tempattack = []
    
    white, black, green, red= (230,196,146),(84,54,36),(0,153,76),(255,0,0)

    selected = (-1, -1)
    isSelected = False

    def __init__(self, side: bool = True, size: int = 600, flip: bool = False):
        init()
        self.new = Board()
        self.flip = flip
        self.m = True
        self.side = side
        self.turn = True
        self.size = (size // 8) * 8
        self.square = size//8
        self.pieceSize = size//10
        self.cent = (self.square - self.pieceSize)//2
        self.chesspieces = load_images('style/pixle')
        for pieces in self.chesspieces:
            self.chesspieces[pieces] = transform.scale(self.chesspieces[pieces], (self.pieceSize, self.pieceSize))
        self.text = font.Font('Fonts\ka1.ttf', self.square//2)
        self.screen = display.set_mode((size, size))

    def gameOver(self, whiteWin: bool, draw: bool = False):
        print("game over") #TODO
        if draw: print("Draw")
        elif whiteWin: print("white won")
        else: print("balck won") 

    def markCheck(self, side: bool = True):
        if self.flip: 
            if side: side = self.turn
            else: side = not self.turn
        if self.new.inCheck(True):
            x,y = self.new.listPos(self.new.locateKing(True))
            if not side: x, y = 7-x, 7-y
            draw.rect(self.screen, self.red, (y*self.square, x*self.square, self.square, self.square), self.square//16)
        elif self.new.inCheck(False):
            x,y = self.new.listPos(self.new.locateKing(False))
            if not side: x, y = 7-x, 7-y
            draw.rect(self.screen, self.red, (y*self.square, x*self.square, self.square, self.square), self.square//16)

    def menu(self):
        draw.rect(self.screen, self.white, (0, 0, self.size, self.size))
        play = self.text.render(("Play"), True,(255,255,255))
        playGrey = self.text.render(("Play"), True,(230,230,230))
        q = self.text.render(("Quit"), True,(255,255,255))
        qGrey = self.text.render(("Quit"), True,(230,230,230))
        clickb=Rect(self.size//2-self.square,self.size//2+self.square//20,self.square*5//3,self.square//2)
        clickq=Rect(self.size//2-self.square,self.size//2+self.pieceSize,self.square*5//3,self.square//2)
        self.screen.blit(play,(self.size//2-self.square, self.size//2))
        self.screen.blit(q,(self.size//2-self.square+self.pieceSize//10, self.size//2+self.pieceSize))

        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()
        if clickb.collidepoint(mx,my):
            self.screen.blit(playGrey,(self.size//2-self.square, self.size//2))
            if mb[0] == 1:
                self.m = False
        if clickq.collidepoint(mx,my):
            self.screen.blit(qGrey,(self.size//2-self.square+self.pieceSize//10, self.size//2+self.pieceSize))
            if mb[0] == 1:
                quit()
            

    # determine select and selcect move
    def select(self, side: bool = True):
        if self.flip: 
            if side: side = self.turn
            else: side = not self.turn

        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()
        sx, sy = self.selected

        if mb[0]:
            if self.mbhold:
                mx = self.mxhold
                my = self.myhold

            cx,cy = mx // self.square, my // self.square
            sx, sy = cx * self.square, cy * self.square
            if not side:
                sx, sy = cx* self.square, cy*self.square
                cx,cy =  7-cx,  7-cy
                    
            if (self.isSelected):
                for target in self.tempattack + self.tempresult:
                    startx, starty = self.selected[1]//self.square, self.selected[0]//self.square
                    if not side:    startx, starty = 7 - startx, 7 - starty
                    start = self.new.chessPos(startx, starty)
                    if self.new.chessPos(cy,cx) == target and self.new.move(start,target):
                        self.turn = not self.turn


            if (self.turn and (self.new.colour(self.new.chessPos(cy,cx)) == 1)) or (not self.turn and (self.new.colour(self.new.chessPos(cy,cx)) == 2)):
                self.tempresult, self.tempattack = self.new.legal(self.new.chessPos(cy,cx))
            else:
                self.tempresult, self.tempattack = [],[]
 
            self.isSelected = True
            self.selected = sx, sy
            
        if (self.isSelected):
            draw.rect(self.screen, self.green, (sx, sy, self.square, self.square), self.square//16)
            for i in self.tempresult:
                tempx, tempy = self.new.listPos(i)
                if side: tempx, tempy = tempx * self.square, tempy * self.square
                else: tempx, tempy = self.size - tempx * self.square - self.square, self.size - tempy * self.square - self.square
                draw.circle(self.screen, self.green, (tempy + self.square//2, tempx + self.square//2), self.square//7)
            for i in self.tempattack:
                tempx, tempy = self.new.listPos(i)
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

    def draw_base(self):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2:
                    draw.rect(self.screen,self.black,(i*self.square,j*self.square,self.square, self.square))
                else:
                    draw.rect(self.screen,self.white,(i*self.square,j*self.square,self.square, self.square))
 
    def draw_board(self, side: bool = True):
        self.draw_base()
        if self.flip: 
            if side: side = self.turn
            else: side = not self.turn
        b = self.new.board
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
    #starting side
    side = True
    g1 = play(side,flip = False)
    run = True
    while run:
        for e in event.get():       
            if e.type == QUIT:      
                run=False
            elif e.type == KEYDOWN and e.key == K_LEFT:
                if g1.new.back():
                    g1.turn = not g1.turn
            elif e.type == KEYDOWN and e.key == K_q:
                g1.m = True
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 3:
                    g1.isSelected = False
                    g1.selected = (-1,-1)
    

        if g1.m:
            g1.menu()
        else:
            g1.draw_board(side)
            g1.markCheck(side)
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
        display.flip()
    quit()


if __name__ == "__main__":
    main()

