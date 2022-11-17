from copy import deepcopy

def char_range(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

# Lowercase for Black pieces, uppercase for White, 'N' is for knight
class board:
    def __init__(self):

        self.whitePieces = ['R','N','B','Q','K','P']
        self.blackPieces = ['r','n','b','q','k','p']

        # Stops infinite recursion while calculating can king castle
        self.recur = True

        self.whiteCastle = True
        self.blackCastle = True
        self.whiteCastleLong = True
        self.blackCastleLong = True

        self.repeatedMoves = 0

        self.state = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']]

        self.history = []
        self.previousState = self.state
    
    # Side is True for white, False for black
    def print_board(self, side: bool = True):
        order = range(8, 0, -1)
        if not side: order = reversed(order)
        for i in order:
            print('  ---------------------------------\n'+ str(i) +' | ', end = '')
            for j in self.state[8-i]:
                if j == '0':
                    print(' ', end = ' | ')
                else:
                    print (j, end = ' | ')
            print('') # prints new line after each row
        print('  ---------------------------------\n    a   b   c   d   e   f   g   h')

    
    def isEnemy(self, squareOne: str, squareTwo: str) -> bool:
        pieceOne = self.name(squareOne)
        pieceTwo = self.name(squareTwo)
        if pieceOne == 'X' or pieceTwo == 'X':
            return pieceOne == 'P' or pieceTwo == 'P' or pieceOne == 'p' or pieceTwo == 'p'
        elif pieceOne in self.whitePieces:
            return pieceTwo in self.blackPieces
        elif pieceTwo in self.whitePieces:
            return pieceOne in self.blackPieces
        else:
            return False

    # Returns position of square name in state, for example chessPos('a1') returns 7, 0
    def listPos(self, square: str) -> tuple[int, int]:
        row = ord('8') - ord(square[1])
        col = ord(square[0]) - ord('a')
        return row, col

    # Inverse of chessPos for exaxmple listPos(7,0) returns 'a1'
    def chessPos(self, row: int, col: int) -> str:
        return chr(ord('a') + col) + chr(ord('8') - row)
    
    # returns 0 for empty, 1 for white, 2 for black
    def colour(self, sq: str) -> int:
        row, col = self.listPos(sq)
        if row > 7 or row < 0 or col < 0 or col > 7:
            return 3
        val = self.name(sq)
        if val == '0' or val == 'X':
            return 0
        elif val.isupper(): return 1
        else:               return 2

    # enter square name, changes the value to new, assumes valid input
    def setValue(self, tar: str, new: str):
        x, y = self.listPos(tar)
        self.state[x][y] = new

    # assumes valid moves only, initial and target are between 'a1' to 'h8'
    def move(self, start: str, target: str):

        # for backtracking moves
        self.previousState = self.state

        # if taking a pieces, state cannot repeat thus clearing previous stored states
        if self.isEnemy(start, target): self.history.clear(); self.repeatedMoves = 0

        # Removes en passant mark
        for i in range(8):
            if self.state[2][i] == 'X': self.state[2][i] = '0'
            if self.state[5][i] == 'X': self.state[5][i] = '0'

        if self.name(start) == 'P' or self.name(start) == 'p':
            # Pawn is moved reset 50 move rule
            self.history.clear()
            self.repeatedMoves = 0

            # When the Pawn moves two square forward, mark the first square to enable En Passant on the next move
            moveOne = self.look(start, 0, self.colour(start) == 1)
            moveTwo = self.look(moveOne, 0, self.colour(start) == 1)
            if target == moveTwo:  self.setValue(moveOne, 'X')

        elif self.name(start) == 'K':
            if self.whiteCastle and target == 'g1':
                self.setValue('f1', 'R')
                self.setValue('h1', '0')
            elif self.whiteCastleLong and target == 'c1':
                self.setValue('d1', 'R')
                self.setValue('a1', '0')

        elif self.name(start) == 'k':
            if self.blackCastle and target == 'g8':
                self.setValue('f8', 'r')
                self.setValue('h8', '0')
            elif self.blackCastleLong and target == 'c8':
                self.setValue('d8', 'r')
                self.setValue('a8', '0')

        self.setValue(target, self.name(start))
        self.setValue(start, '0')
            
        # automatically promote to queen
        for i in range(8):
            if self.state[0][i] == 'P':
                self.state[0][i] = 'Q'
            if self.state[7][i] == 'p':
                self.state[7][i] = 'q'
        
        # When rook is moved that colour can no longer castle that side
        # when king is moved that colour can no longer castle at all
        if start == 'h1' or start == 'e1': self.whiteCastle = False
        if start == 'a1' or start == 'e1': self.whiteCastleLong = False
        if start == 'h8' or start == 'e8': self.blackCastle = False
        if start == 'a8' or start == 'e8': self.blackCastleLong = False
        
        tempmax = 0
        for i in self.history:
            count = 0
            for j in self.history:
                if i == j:
                    count += 1
                    tempmax = max(tempmax, count)
        self.repeatedMoves = max(tempmax, self.repeatedMoves)
        newstate = ""
        for i in self.state:
            tempstate = ""
            for j in i:
                tempstate = tempstate + j
            newstate = newstate + tempstate
        self.history.append(newstate)


    # returns pos of piece in chosen dir, returns '00' if hitting wall
    def look(self, target: str, direction: int, forward: bool = True) -> str:

        if not forward:
            if direction == 1 or direction == 0: direction = 1 - direction
            else: direction = 5 - direction

        a = target[0]
        b = target[1]

        match direction:
            case 0: b = chr(ord(b) + 1)
            case 1: b = chr(ord(b) - 1)
            case 2: a = chr(ord(a) - 1)
            case 3: a = chr(ord(a) + 1)

        if ('a' <= a <= 'h') and ('1' <= b <= '8'):
            return a + b
        else:   return '00'

    # returns true if safe else false
    def moveTest(self, start: str, target: str) -> bool:
        temp = deepcopy(self)
        temp.move(start, target)
        return not temp.inCheck(self.colour(start) == 1)
        

    def name(self, target: str) -> str:
        if not (('a' <= target[0] <= 'h') and ('1' <= target[1] <= '8')):
            return 'W'
        else:
            a, b = self.listPos(target)
            return self.state[a][b]

    # assumes kings always exist, side = True if white, else black 
    def locateKing(self, side: bool) -> str:
        if side: king = 'K'
        else: king = 'k'
        temp = self.state
        for row in temp:
            if king in row:
                return self.chessPos(temp.index(row), row.index(king))
    
           
    def inCheck(self, side: bool) -> bool:
        loc = self.locateKing(side)
        return self.isSafe(side, loc)

    def isMate(self, side: bool) -> bool:
        side = not side
        if not self.inCheck(side):
            return False
        if side:    clr = 1
        else:       clr = 2
        for i in char_range('a','h'):
            for j in char_range('1','8'):
                k = i + j
                if (self.colour(k) == clr):
                    t1, t2 = self.legal(k)
                    t3 = t1 + t2
                    for l in t3:
                        temp = deepcopy(self)
                        temp.move(k, l)
                        if not temp.inCheck(side):
                            return False
        return True


    def isDraw(self, side: bool) -> bool:
        if len(self.history) >= 50: return True
        if self.repeatedMoves >= 3: return True
        side = not side
        c = self.inCheck(side)
        if side:    clr = 1
        else:       clr = 2
        for i in char_range('a','h'):
            for j in char_range('1','8'):
                k = i + j
                if (self.colour(k) == clr):
                    t1, t2 = self.legal(k)
                    t3 = t1 + t2
                    for l in t3:
                        temp = deepcopy(self)
                        temp.move(k, l)
                        if not temp.inCheck(side):
                            return False 
        return not c

    def rookHelper(self, target: str) -> tuple[list[str], list[str]]:
        attack = []
        result = []
        pos1 = self.look(target, 0)
        pos2 = self.look(target, 1) 
        pos3 = self.look(target, 2)
        pos4 = self.look(target, 3)
        while self.colour(pos1) == 0:
            result.append(pos1)
            pos1 = self.look(pos1,0)
        while self.colour(pos2) == 0:
            result.append(pos2)
            pos2 = self.look(pos2,1)
        while self.colour(pos3) == 0:
            result.append(pos3)
            pos3 = self.look(pos3,2)
        while self.colour(pos4) == 0:
            result.append(pos4)
            pos4 = self.look(pos4,3)
        if self.isEnemy(pos1, target): attack.append(pos1)
        if self.isEnemy(pos2, target): attack.append(pos2)
        if self.isEnemy(pos3, target): attack.append(pos3)
        if self.isEnemy(pos4, target): attack.append(pos4)
        return result, attack

    def bishopHelper(self, target: str) -> tuple[list[str],list[str]]:
        result = []
        attack = []
        t1 = self.look(target, 0)
        t2 = self.look(target, 1)
        pos1 = self.look(t1, 2)
        pos2 = self.look(t1, 3) 
        pos3 = self.look(t2, 2)
        pos4 = self.look(t2, 3)
        while self.colour(pos1) == 0:
            result.append(pos1)
            pos1 = self.look(self.look(pos1,0),2)
        while self.colour(pos2) == 0:
            result.append(pos2)
            pos2 = self.look(self.look(pos2,0),3)
        while self.colour(pos3) == 0:
            result.append(pos3)
            pos3 = self.look(self.look(pos3,1),2)
        while self.colour(pos4) == 0:
            result.append(pos4)
            pos4 = self.look(self.look(pos4,1),3)
        if self.isEnemy(pos1, target): attack.append(pos1)
        if self.isEnemy(pos2, target): attack.append(pos2)
        if self.isEnemy(pos3, target): attack.append(pos3)
        if self.isEnemy(pos4, target): attack.append(pos4)
        return result, attack

    def knightHelper(self, target: str) -> tuple[list[str], list[str]]:
        possible = []
        result = []
        attack = []
        t1 = self.look(target, 0)
        t2 = self.look(target, 1)
        t3 = self.look(target, 2)
        t4 = self.look(target, 3)
        possible.append(self.look(self.look(t1, 2), 2))
        possible.append(self.look(self.look(t1, 3), 3))
        possible.append(self.look(self.look(t2, 2), 2))
        possible.append(self.look(self.look(t2, 3), 3))
        possible.append(self.look(self.look(t3, 1), 1))
        possible.append(self.look(self.look(t3, 0), 0))
        possible.append(self.look(self.look(t4, 0), 0))
        possible.append(self.look(self.look(t4, 1), 1))

        for i in possible:
            if (i != '00'):
                if (self.colour(i) == 0):
                    result.append(i)
                elif self.isEnemy(i, target):
                    attack.append(i)
        return result, attack

    def kingHelper(self, target: str) -> tuple[list[str], list[str]]:
        clr = self.colour(target)
        possible = []
        result = []
        attack = []
        up = self.look(target,0)
        down = self.look(target,1)
        left = self.look(target,2)
        right = self.look(target,3)
        upleft = self.look(up, 2)
        upright = self.look(up, 3)
        downleft = self.look(down,2)
        downright = self.look(down,3)
        possible.append(up)
        possible.append(down)
        possible.append(left)
        possible.append(right)
        possible.append(upleft)
        possible.append(upright) 
        possible.append(downleft)
        possible.append(downright)

        # Castle check
        leftleft = self.look(left, 2)
        rightright = self.look(right, 3)

        if self.recur:
            self.recur = False
            dan = self.danger(clr == 1)
            if (self.whiteCastle and clr == 1) or (self.blackCastleLong and clr == 2):
                if self.colour(right) == 0 and self.colour(rightright) == 0 and (rightright not in dan) and (right not in dan) and (target not in dan):
                    possible.append(self.look(right,3))
            if (self.whiteCastleLong and clr == 1) or (self.blackCastle and clr == 2):
                if self.colour(left) == 0 and self.colour(leftleft) == 0 and (leftleft not in dan) and (left not in dan) and (target not in dan):
                    possible.append(self.look(left,2))
            self.recur = True

        for i in possible:
            if (i != '00'):
                if (self.colour(i) == 0):
                    result.append(i)
                elif (self.isEnemy(target, i)):
                    attack.append(i)

        return result, attack

    def pawnHelper(self, target: str) -> tuple[list[str], list[str]]:
        result = []
        attack = []
        side = self.colour(target) == 1
        pos1 = self.look(target, 0, side) # 1 sqaure front of target
        pos2 = self.look(pos1, 0, side)   # 2 squares front of target
        pos3 = self.look(pos1, 2)
        pos4 = self.look(pos1, 3)
        if self.name(pos1) == '0':
            result.append(pos1)
            if self.name(pos2) == '0':
                # When white pawn is on 7th row or black pawn is on 2nd row, they can move two squares
                if (target[1] == '2'  and self.name(target) == 'P') or (target[1] == '7' and self.name(target) == 'p'):
                    result.append(pos2)
        if self.isEnemy(pos3, target): attack.append(pos3)
        if self.isEnemy(pos4,target): attack.append(pos4)
        return result, attack

    # Input a position of a piece and return two list of all posible position
    def legal(self, target: str) -> tuple[list[str], list[str]]:
        piece = self.name(target)
        match piece:
            case 'P' | 'p':
                result, attack = self.pawnHelper(target)
            case 'R' | 'r':
                result, attack = self.rookHelper(target)
            case 'B' | 'b':
                result, attack = self.bishopHelper(target)
            case 'Q' | 'q':
                rresult, rattack = self.rookHelper(target)
                bresult, battack = self.bishopHelper(target)
                result = bresult + rresult
                attack = battack + rattack
            case 'N' | 'n':
                result, attack = self.knightHelper(target)
            case 'K' | 'k':
                result, attack = self.kingHelper(target)

        return result, attack

    def isSafe(self, side: bool, target: str) -> bool:
        return (target in self.danger(side))

    def danger(self, side: bool) -> list[str]:
        if side:    clr = 1
        else:       clr = 2
        bad = []
        for i in char_range('a','h'):
            for j in char_range('1','8'):
                k = i + j
                if (clr * self.colour(k) == 2):
                    result, attack = self.legal(k)
                    bad = bad + attack + result
        return attack + result

## TODO: add menu, add backtracks, stay on the same square after moving when flipping sides