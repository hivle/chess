import os
from game import board
from pygame import *
 
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
    bishop = image.load(os.path.join('style','pixle','bishop.png'))
    bishop1 = image.load(os.path.join('style','pixle','bishop1.png'))
    king = image.load(os.path.join('style','pixle','king.png'))
    king1 = image.load(os.path.join('style','pixle','king1.png'))
    knight = image.load(os.path.join('style','pixle','knight.png'))
    knight1 = image.load(os.path.join('style','pixle','knight1.png'))
    pawn = image.load(os.path.join('style','pixle','pawn.png'))
    pawn1 = image.load(os.path.join('style','pixle','pawn1.png'))
    queen = image.load(os.path.join('style','pixle','queen.png'))
    queen1 = image.load(os.path.join('style','pixle','queen1.png'))
    rook = image.load(os.path.join('style','pixle','rook.png'))
    rook1 = image.load(os.path.join('style','pixle','rook1.png'))
    
    selected = (-1, -1)
    isSelected = False

    def __init__(self, side: bool = True, size: int = 600):
        self.size = (size // 8) * 8
        self.square = size//8
        self.pieceSize = size//10
        self.cent = (self.square - self.pieceSize)//2
        self.bishop = transform.scale(self.bishop, (self.pieceSize, self.pieceSize))
        self.bishop1 = transform.scale(self.bishop1, (self.pieceSize, self.pieceSize))
        self.king = transform.scale(self.king, (self.pieceSize, self.pieceSize))
        self.king1 = transform.scale(self.king1, (self.pieceSize, self.pieceSize))
        self.knight = transform.scale(self.knight, (self.pieceSize, self.pieceSize))
        self.knight1 = transform.scale(self.knight1, (self.pieceSize, self.pieceSize))
        self.pawn = transform.scale(self.pawn, (self.pieceSize, self.pieceSize))
        self.pawn1 = transform.scale(self.pawn1, (self.pieceSize, self.pieceSize))
        self.queen = transform.scale(self.queen, (self.pieceSize, self.pieceSize))
        self.queen1 = transform.scale(self.queen1, (self.pieceSize, self.pieceSize))
        self.rook = transform.scale(self.rook, (self.pieceSize, self.pieceSize))
        self.rook1 = transform.scale(self.rook1, (self.pieceSize, self.pieceSize))

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
                        self.new.print_board()
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

    
    def draw_board(self, side: bool = True):
        sq = []
        for i in range(7):
            if i % 2 == 0:
                sq.append(i * self.square) 
        b = self.new.state
        if side:
            for i in sq:
                for j in sq:
                    draw.rect(self.screen,self.white,(i,j,self.square, self.square))
                    draw.rect(self.screen,self.black,(i+self.square,j,self.square,self.square))
                    draw.rect(self.screen,self.black,(i,j+self.square,self.square,self.square))
                    draw.rect(self.screen,self.white,(i+self.square,j+self.square,self.square,self.square))
            row = 0
            for i in b:
                col = 0
                for piece in i:
                    match piece:
                        case 'P':
                            self.screen.blit(self.pawn,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'R':
                            self.screen.blit(self.rook,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'B':
                            self.screen.blit(self.bishop,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'Q':
                            self.screen.blit(self.queen,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'N':
                            self.screen.blit(self.knight,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'K':
                            self.screen.blit(self.king,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'p':
                            self.screen.blit(self.pawn1,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'r':
                            self.screen.blit(self.rook1,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'b':
                            self.screen.blit(self.bishop1,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'q':
                            self.screen.blit(self.queen1,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'n':
                            self.screen.blit(self.knight1,(col * self.square + self.cent,row * self.square + self.cent))
                        case 'k':
                            self.screen.blit(self.king1,(col * self.square + self.cent,row * self.square + self.cent))
                    col += 1
                row += 1
        else:
            for i in sq:
                for j in sq:
                    draw.rect(self.screen,self.black,(i,j,self.square, self.square))
                    draw.rect(self.screen,self.white,(i+self.square,j,self.square,self.square))
                    draw.rect(self.screen,self.white,(i,j+self.square,self.square,self.square))
                    draw.rect(self.screen,self.black,(i+self.square,j+self.square,self.square,self.square))
            row = 0
            for i in b:
                col = 0
                for piece in i:
                    match piece:
                        case 'P':
                            self.screen.blit(self.pawn,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'R':
                            self.screen.blit(self.rook,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'B':
                            self.screen.blit(self.bishop,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'Q':
                            self.screen.blit(self.queen,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'N':
                            self.screen.blit(self.knight,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'K':
                            self.screen.blit(self.king,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'p':
                            self.screen.blit(self.pawn1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'r':
                            self.screen.blit(self.rook1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'b':
                            self.screen.blit(self.bishop1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'q':
                            self.screen.blit(self.queen1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'n':
                            self.screen.blit(self.knight1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                        case 'k':
                            self.screen.blit(self.king1,(self.size - (col+1) * self.square + self.cent, self.size - (row+1) * self.square + self.cent))
                    col += 1
                row += 1
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

