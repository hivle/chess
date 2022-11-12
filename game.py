from copy import deepcopy

def char_range(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

# Lowercase for Black pieces, uppercase for White, 'N' is for knight
class board:
    def __init__(self):
        self.turn = True # True for white, False for black
        self.white_castle = True
        self.black_castle = True

        self.state = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']]
        self.white_taken = []
        self.black_taken = []
        self.history = []
    
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

    # Returns position of square name in state, for example chessPos('a1') returns 7, 0
    def chessPos(self, sq: str) -> tuple[int, int]:
        row = ord('8') - ord(sq[1])
        col = ord(sq[0]) - ord('a')
        return row, col

    # Inverse of chessPos for exaxmple listPos(7,0) returns 'a1'
    def listPos(self, row: int, col: int) -> str:
        return chr(ord('a') + col) + chr(ord('8') - row)
    
    # returns 0 for empty, 1 for white, 2 for black
    def colour(self, sq: str) -> int:
        row, col = self.chessPos(sq)
        if row > 7 or row < 0 or col < 0 or col > 7:
            return 0
        val = self.state[row][col]
        if val == '0':      return 0
        elif val.isupper(): return 1
        else:               return 2
    
    def move(self, initial: str, target: str) -> bool:
        colini = self.colour(initial)
        coltar = self.colour(target)
        if (not (colini == coltar) and not(colini == 0)):
            inir, inic = self.chessPos(initial)
            tarr, tarc = self.chessPos(target)
            piece = self.state[inir][inic]
            self.state[tarr][tarc] = piece
            self.state[inir][inic] = '0'
            return True
        else:
            return False

    # 0 for up, 1 for down, 2 for left, 3 for right
    # returns pos of next piece, returns '00' if hitting wall
    def walk(self, target: str, dir: int) -> str:
        if not (('a' <= target[0] <= 'h') and ('1' <= target[1] <= '8')):
            return '00'
        a = target[0]
        b = target[1]
        match dir:
            case 0: b = chr(ord(b) + 1)
            case 1: b = chr(ord(b) - 1)
            case 2: a = chr(ord(a) - 1)
            case 3: a = chr(ord(a) + 1)
        if (('a' <= a <= 'h') and ('1' <= b <= '8')):
            return a + b
        else:
            return '00'

    def name(self, target: str) -> str:
        if not (('a' <= target[0] <= 'h') and ('1' <= target[1] <= '8')):
            return 'W'
        else:
            a, b = self.chessPos(target)
            return self.state[a][b]

    # assumes kings always exist, side = True if white, else black 
    def locateKing(self, side: bool) -> str:
        if side: king = 'K'
        else: king = 'k'
        for i in range(8):
            for j in range(8):
                if self.state[i][j] == king:
                    return self.listPos(i, j)
    
           
    def inCheck(self, side: bool) -> bool:
        loc = self.locateKing(side)
        if (loc in self.danger(loc)):
            return True
        else:
            return False

    def isMate(self, side: bool) -> bool:
        loc = self.locateKing(side)
        safe = []
        block = []
        if not self.inCheck(loc):
            return False
        attack = self.kingHelper(loc)[1]
        for i in attack:
            temp = deepcopy(self)
            temp.move(loc, i)
            if not temp.inCheck(side):
                safe.append(i)
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
                            safe.append(l)
        if len(safe) == 0 and len (block) == 0:
            return True
        return False


    def rookHelper(self, target: str) -> tuple[list[str], list[str]]:
        clr = self.colour(target)
        attack = []
        result = []
        pos1 = self.walk(target, 0)
        pos2 = self.walk(target, 1) 
        pos3 = self.walk(target, 2)
        pos4 = self.walk(target, 3)
        while self.name(pos1) == '0':
            result.append(pos1)
            pos1 = self.walk(pos1,0)
        while self.name(pos2) == '0':
            result.append(pos2)
            pos2 = self.walk(pos2,1)
        while self.name(pos3) == '0':
            result.append(pos3)
            pos3 = self.walk(pos3,2)
        while self.name(pos4) == '0':
            result.append(pos4)
            pos4 = self.walk(pos4,3)
        if (self.colour(pos1) * clr) == 2: attack.append(pos1)
        if (self.colour(pos2) * clr) == 2: attack.append(pos2)
        if (self.colour(pos3) * clr) == 2: attack.append(pos3)
        if (self.colour(pos4) * clr) == 2: attack.append(pos4)
        return result, attack

    def bishopHelper(self, target: str) -> tuple[list[str],list[str]]:
        clr = self.colour(target)
        result = []
        attack = []
        t1 = self.walk(target, 0)
        t2 = self.walk(target, 1) 
        pos1 = self.walk(t1, 2)
        pos2 = self.walk(t1, 3) 
        pos3 = self.walk(t2, 2)
        pos4 = self.walk(t2, 3)
        while self.name(pos1) == '0':
            result.append(pos1)
            pos1 = self.walk(self.walk(pos1,0),2)
        while self.name(pos2) == '0':
            result.append(pos2)
            pos2 = self.walk(self.walk(pos2,0),3)
        while self.name(pos3) == '0':
            result.append(pos3)
            pos3 = self.walk(self.walk(pos3,1),2)
        while self.name(pos4) == '0':
            result.append(pos4)
            pos4 = self.walk(self.walk(pos4,1),3)
        if (self.colour(pos1) * clr) == 2: attack.append(pos1)
        if (self.colour(pos2) * clr) == 2: attack.append(pos2)
        if (self.colour(pos3) * clr) == 2: attack.append(pos3)
        if (self.colour(pos4) * clr) == 2: attack.append(pos4)
        return result, attack

    def knightHelper(self, target: str):
        clr = self.colour(target)
        possible = []
        result = []
        attack = []
        t1 = self.walk(target, 0)
        t2 = self.walk(target, 1) 
        t3 = self.walk(target, 2)
        t4 = self.walk(target, 3)
        possible.append(self.walk(self.walk(t1, 2), 2))
        possible.append(self.walk(self.walk(t1, 3), 3))
        possible.append(self.walk(self.walk(t2, 2), 2))
        possible.append(self.walk(self.walk(t2, 3), 3))
        possible.append(self.walk(self.walk(t3, 1), 1))
        possible.append(self.walk(self.walk(t3, 0), 0))
        possible.append(self.walk(self.walk(t4, 0), 0))
        possible.append(self.walk(self.walk(t4, 1), 1))
        for i in possible:
            if (i != '00'):
                if (self.colour(i) == 0):
                    result.append(i)
                elif (self.colour(i) * clr == 2):
                    attack.append(i)
        return result, attack

    def kingHelper(self, target: str):
        clr = self.colour(target)
        possible = []
        result = []
        attack = []
        up = self.walk(target,0)
        down = self.walk(target,1)
        left = self.walk(target,2)
        right = self.walk(target,3)
        upleft = self.walk(up, 2)
        upright = self.walk(up, 3)
        downleft = self.walk(down,2)
        downright = self.walk(down,3)
        possible.append(up)
        possible.append(down)
        possible.append(left)
        possible.append(right)
        possible.append(upleft)
        possible.append(upright) 
        possible.append(downleft)
        possible.append(downright)
        for i in possible:
            if (i != '00'):
                if (self.colour(i) == 0):
                    result.append(i)
                elif (self.colour(i) * clr == 2):
                    attack.append(i)
        return result, attack

    # Input a position of a piece and return two list of all posible position
    def legal(self, target: str) -> tuple[list[str], list[str]]:
        piece = self.name(target)
        clr = self.colour(target)
        result = []
        attack = []
        match piece:
            case 'P' | 'p':
                pos1 = self.walk(target, clr - 1) # 1 sqaure front of target
                pos2 = self.walk(pos1, clr - 1)   # 2 squares front of target
                pos3 = self.walk(pos1, 2)
                pos4 = self.walk(pos1, 3)
                if self.name(pos1) == '0':
                    result.append(pos1)
                    if(self.name(pos2) == '0'):
                        if (target[1] == '2'  and piece == 'P') or (target[1] == '7' and piece == 'p'):
                            result.append(pos2)
                if (pos3 != '00'): attack.append(pos3)
                if (pos4 != '00'): attack.append(pos4)
                return result, attack
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

    def danger(self, side: bool) -> list[str]:
        if side:    clr = 1
        else:       clr = 2
        bad = []
        for i in char_range('a','h'):
            for j in char_range('1','8'):
                k = i + j
                if (clr * self.colour(k) == 2):
                    result, attack = self.legal(k)
                    bad = bad + result + attack
        bad = list(set(bad))
        return bad
