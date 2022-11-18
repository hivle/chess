from copy import deepcopy
from itertools import permutations, product
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
    
    # returns 0 for empty, 1 for white, 2 for black, 3 for out of range
    def colour(self, sq: str) -> int:
        val = self.name(sq)
        if val in self.whitePieces:
            return 1
        elif val in self.blackPieces:
            return 2
        elif val == '0' or val == 'X':
            return 0
        elif val == 'W':
            return 3

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
            one = self.look(start, (0,1), self.colour(start) == 1)
            two = self.look(one, (0,1), self.colour(start) == 1)
            if target == two:  self.setValue(one, 'X')

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
    def look(self, target: str, direction: tuple[int, int], forward: bool = True) -> str:

        if not forward:
            direction = (-direction[0], -direction [1])

        letter = target[0]
        number = target[1]

        letter = chr(ord(letter) + direction[0])
        number = chr(ord(number) + direction [1])

        if ('a' <= letter <= 'h') and ('1' <= number <= '8'):
            return letter + number
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
        result = []
        attack = []
        for direction in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            current = self.look(target, direction)
            while self.colour(current) == 0:
                result.append(current)
                current = self.look(current, direction)
            if self.isEnemy(current, target): attack.append(current)
        return result, attack

    def bishopHelper(self, target: str) -> tuple[list[str],list[str]]:
        result = []
        attack = []
        for direction in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
            current = self.look(target, direction)
            while self.colour(current) == 0:
                result.append(current)
                current = self.look(current, direction)
            if self.isEnemy(current, target): attack.append(current)
        return result, attack

    def knightHelper(self, target: str) -> tuple[list[str], list[str]]:
        result = []
        attack = []
        for direction in permutations([-1,1,-2,2],2):
            if abs(direction[0]) != abs(direction[1]):
                move = self.look(target, direction)
                if (move != '00'):
                    if (self.colour(move) == 0):
                        result.append(move)
                    elif self.isEnemy(move, target):
                        attack.append(move)
        return result, attack

    def kingHelper(self, target: str) -> tuple[list[str], list[str]]:
        clr = self.colour(target)
        result = []
        attack = []

        # Castle check
        left = self.look(target,(-1,0), clr == 1)
        right = self.look(target,(1,0), clr == 1)
        leftleft = self.look(target, (-2,0), clr == 1)
        rightright = self.look(target, (2,0),clr == 1)

        if self.recur:
            self.recur = False
            dan = self.danger(clr == 1)
            if (self.whiteCastle and clr == 1) or (self.blackCastleLong and clr == 2):
                if self.colour(right) == 0 and self.colour(rightright) == 0 and (rightright not in dan) and (right not in dan) and (target not in dan):
                    result.append(rightright)
            if (self.whiteCastleLong and clr == 1) or (self.blackCastle and clr == 2):
                if self.colour(left) == 0 and self.colour(leftleft) == 0 and (leftleft not in dan) and (left not in dan) and (target not in dan):
                    result.append(leftleft)
            self.recur = True

        for direction in (list(product([1,-1,0],[1,-1,0]))):
            if direction != (0,0):
                move = self.look(target, direction)
                if (move != '00'):
                    if (self.colour(move) == 0):
                        result.append(move)
                    elif self.isEnemy(move, target):
                        attack.append(move)

        return result, attack

    def pawnHelper(self, target: str) -> tuple[list[str], list[str]]:
        result = []
        attack = []
        side = self.colour(target) == 1
        pos1 = self.look(target, (0,1), side) # 1 sqaure front of target
        pos2 = self.look(pos1, (0,1), side)   # 2 squares front of target
        pos3 = self.look(target, (1,1), side)
        pos4 = self.look(target, (-1,1), side)
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
        bad = []
        enemyColour = 1
        if side: enemyColour = 2
        for i in char_range('a','h'):
            for j in char_range('1','8'):
                k = i + j
                if self.colour(k) == enemyColour:
                    result, attack = self.legal(k)
                    bad = bad + result + attack
        list(set(bad))
        return bad

## TODO: add menu, add backtracks, stay on the same square after moving when flipping sides