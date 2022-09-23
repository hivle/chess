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

    def chessPos(self, sq: str) -> tuple[int, int]:
        row = ord('8') - ord(sq[1])
        col = ord(sq[0]) - ord('a')
        return row, col

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
    
    def move(self, initial: str, target: str):
        colini = self.colour(initial)
        coltar = self.colour(target)
        if (not (colini == coltar) and not(colini == 0)):
            inir, inic = self.chessPos(initial)
            tarr, tarc = self.chessPos(target)
            piece = self.state[inir][inic]
            self.state[tarr][tarc] = piece
            self.state[inir][inic] = '0'

    # 0 for up, 1 for down, 2 for left, 3 for right
    # returns pos of next piece, returns '00' if hitting wall
    def look(self, target: str, dir: int) -> str:
        a, b= self.chessPos(target)
        match dir:
            case 0:
                if a == 0: return '00'
                a -= 1
            case 1:
                if a == 7: return '00'
                a += 1
            case 2:
                if b == 0: return '00'
                b -= 1
            case 3:
                if b == 7: return '00'
                b += 1
        return self.listPos(a,b)

    def name(self, target: str) -> str:
        if target == '00': return 'W'
        else:
            a, b = self.chessPos(target)
            return self.state[a][b]

    # assumes kings always exist, side = True if white, else black 
    def locateKing(self, side: bool) -> str:
        if side: king = 'K'
        else: king = 'k'
        for i in range(8):
            for j in self.state[i]:
                if j == king:
                    return self.listPos(i, j)
    
           
    # def inCheck(self, side: bool) -> bool:
    #     loc = self.locateKing(side)
        
                
        # up = self.look(loc,0)
        # down = self.look(loc,1)
        # left = self.look(loc,2)
        # right = self.look(loc,3)
        # upleft = self.look(up, 2)
        # upright = self.look(up, 3)
        # downleft = self.look(down,2)
        # downright = self.look(down,3)

    def rookHelper(self, clr: int, target: str) -> tuple[list[str], list[str]]:
        attack = []
        result = []
        pos1 = self.look(target, 0)
        pos2 = self.look(target, 1) 
        pos3 = self.look(target, 2)
        pos4 = self.look(target, 3)
        while self.name(pos1) == '0':
            result.append(pos1)
            pos1 = self.look(pos1,0)
        while self.name(pos2) == '0':
            result.append(pos2)
            pos2 = self.look(pos2,1)
        while self.name(pos3) == '0':
            result.append(pos3)
            pos3 = self.look(pos3,2)
        while self.name(pos4) == '0':
            result.append(pos4)
            pos4 = self.look(pos4,3)
        if (self.colour(pos1) + clr)%2 == 0: attack.append(pos1)
        if (self.colour(pos2) + clr)%2 == 0: attack.append(pos2)
        if (self.colour(pos3) + clr)%2 == 0: attack.append(pos3)
        if (self.colour(pos4) + clr)%2 == 0: attack.append(pos4)
        return result, attack

    def bishopHelper(self, clr: int, target: str) -> tuple[list[str],list[str]]:
        result = []
        attack = []
        t1 = self.look(target, 0)
        t2 = self.look(target, 1) 
        pos1 = self.look(t1, 2)
        pos2 = self.look(t1, 3) 
        pos3 = self.look(t2, 2)
        pos4 = self.look(t2, 3)
        while self.name(pos1) == '0':
            result.append(pos1)
            pos1 = self.look(self.look(pos1,0),2)
        while self.name(pos2) == '0':
            result.append(pos2)
            pos2 = self.look(self.look(pos2,0),3)
        while self.name(pos3) == '0':
            result.append(pos3)
            pos3 = self.look(self.look(pos3,1),2)
        while self.name(pos4) == '0':
            result.append(pos4)
            pos4 = self.look(self.look(pos4,1),3)
        if (self.colour(pos1) + clr)%2 == 0: attack.append(pos1)
        if (self.colour(pos2) + clr)%2 == 0: attack.append(pos2)
        if (self.colour(pos3) + clr)%2 == 0: attack.append(pos3)
        if (self.colour(pos4) + clr)%2 == 0: attack.append(pos4)
        return result, attack

    # Input a position of a piece and return two list of all posible position
    def legal(self, target: str) -> tuple[list[str], list[str]]:
        piece = self.name(target)
        clr = self.colour(target)
        result = []
        attack = []
        match piece:
            case 'P' | 'p':
                pos1 = self.look(target, clr - 1) # 1 sqaure front of target
                pos2 = self.look(pos1, clr - 1)   # 2 squares front of target
                pos3 = self.look(pos1, 2)
                pos4 = self.look(pos1, 3)
                if self.name(pos1) == '0':
                    result.append(pos1)
                    if (target[1] == '2' and self.name(pos2) == '0'): result.append(pos2)
                if (not pos3 == '00'): attack.append(pos3)
                if (not pos4 == '00'): attack.append(pos4)
                return result, attack
            case 'R' | 'r':
                rresult, rattack = self.rookHelper(clr, target)
                result = result + rresult
                attack = attack + rattack
            case 'B' | 'b':
                bresult, battack = self.bishopHelper(clr, target)
                result = result + bresult
                attack = attack + battack
            case 'Q' | 'q':
                rresult, rattack = self.rookHelper(clr, target)
                bresult, battack = self.bishopHelper(clr, target)
                result = result + bresult + rresult
                attack = attack + battack + rattack


        print(attack)
        print(result)
