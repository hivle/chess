from copy import deepcopy
from stack import Stack
from itertools import permutations, product


def _charRange(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

# Lowercase for Black pieces, uppercase for White, 'N' is for knight
class Board:
    def __init__(self):

        self._whitePieces = ['R','N','B','Q','K','P']
        self._blackPieces = ['r','n','b','q','k','p']

        self.whiteTurn = True

        self._whiteCastle = True
        self._blackCastle = True
        self._whiteCastleLong = True
        self._blackCastleLong = True

        self._repeatedMoves = 0
        self.gameDraw = False
        self.whiteWin = False

        self.state = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']]

        self.history = Stack()
        self.history.push("rnbqkbnrpppppppp00000000000000000000000000000000PPPPPPPPRNBQKBNR")
    
    # Side is True for white at bottom, False for black
    def __str__(self, side: bool = True) -> str:
        order = range(8, 0, -1)
        if not side: order = reversed(order)
        result = ""
        for row in order:
            result += f"  ---------------------------------\n" + str(row) + " | "
            for piece in self.state[8 - row]:
                if piece == '0':
                    result += "  | "
                else:
                    result = result + piece + " | "
            result += "\n" # prints new line after each row
        result += "  ---------------------------------\n    a   b   c   d   e   f   g   h\n"
        return result
    
    def isEnemy(self, squareOne: str, squareTwo: str) -> bool:
        pieceOne = self.name(squareOne)
        pieceTwo = self.name(squareTwo)
        if pieceOne == 'X' or pieceTwo == 'X':
            return pieceOne == 'P' or pieceTwo == 'P' or pieceOne == 'p' or pieceTwo == 'p'
        elif pieceOne in self._whitePieces:
            return pieceTwo in self._blackPieces
        elif pieceTwo in self._whitePieces:
            return pieceOne in self._blackPieces
        else:
            return False

    # translate chess coordinates to indexes
    def listPos(self, square: str) -> tuple[int, int]:
        row = ord('8') - ord(square[1])
        col = ord(square[0]) - ord('a')
        return row, col

    # Translate indexes to chess coorinates
    def chessPos(self, row: int, col: int) -> str:
        return chr(ord('a') + col) + chr(ord('8') - row)
    
    # returns 0 for empty, 1 for white, 2 for black, 3 for out of range
    def colour(self, target: str) -> int:
        val = self.name(target)
        if val in self._whitePieces:
            return 1
        elif val in self._blackPieces:
            return 2
        elif val == '0' or val == 'X':
            return 0
        elif val == 'W':
            return 3

    # enter square name, changes the value to new, assumes valid input
    def setValue(self, target: str, new: str):
        x, y = self.listPos(target)
        self.state[x][y] = new

    # assumes valid moves only, initial and target are between 'a1' to 'h8'
    def move(self, start: str, end: str, test: bool = True) -> bool:
        isWhite = self.colour(start) == 1
        if test:
            temp = deepcopy(self)
            temp.move(start, end, False)
            if temp.inCheck(isWhite):
                return False

        self._repeatedMoves += 1
        # if taking a pieces, state cannot repeat thus clearing previous stored states
        if self.isEnemy(start, end): self._repeatedMoves = 0

        # Removes en passant mark
        for i in range(8):
            if self.state[2][i] == 'X': self.state[2][i] = '0'
            if self.state[5][i] == 'X': self.state[5][i] = '0'

        if self.name(start) == 'P' or self.name(start) == 'p':
            # Pawn is moved reset 50 move rule
            self._repeatedMoves = 0

            # When the Pawn moves two square forward, mark the first square to enable En Passant on the next move
            one = self.look(start, (0,1), isWhite)
            two = self.look(one, (0,1), isWhite)
            if end == two:  self.setValue(one, 'X')

        elif self.name(start) == 'K':
            if self._whiteCastle and end == 'g1':
                self.setValue('f1', 'R')
                self.setValue('h1', '0')
            elif self._whiteCastleLong and end == 'c1':
                self.setValue('d1', 'R')
                self.setValue('a1', '0')
            
        elif self.name(start) == 'k':
            if self._blackCastle and end == 'g8':
                self.setValue('f8', 'r')
                self.setValue('h8', '0')
            elif self._blackCastleLong and end == 'c8':
                self.setValue('d8', 'r')
                self.setValue('a8', '0')

        # Setting the value of target square to start piece, and start piece to empty, and switch turns
        self.setValue(end, self.name(start))
        self.setValue(start, '0')
        self.whiteTurn = not self.whiteTurn
            
        # automatically promote to queen
        for i in range(8):
            if self.state[0][i] == 'P':
                self.state[0][i] = 'Q'
            if self.state[7][i] == 'p':
                self.state[7][i] = 'q'
                
        # When rook is moved that colour can no longer castle that side
        # when king is moved that colour can no longer castle at all
        if start == 'h1' or start == 'e1': self._whiteCastle = False
        if start == 'a1' or start == 'e1': self._whiteCastleLong = False
        if start == 'h8' or start == 'e8': self._blackCastle = False
        if start == 'a8' or start == 'e8': self._blackCastleLong = False
        
        newstate = ""
        for i in self.state:
            tempstate = ""
            for j in i:
                tempstate = tempstate + j
            newstate = newstate + tempstate
        self.history.push(newstate)
        if self.history.count(newstate) >= 3:
            self.gameDraw = True
        return True

    def back(self) -> bool:
        last = self.history.pop()
        if last is None:
            return False
        for i in range(8):
            for j in range(8):
                self.state[i][j] = last[i * 8 + j]
        self.whiteTurn = not self.whiteTurn
        self._repeatedMoves -= 1
        return True

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

    def name(self, target: str) -> str:
        if not (('a' <= target[0] <= 'h') and ('1' <= target[1] <= '8')):
            return 'W'
        else:
            a, b = self.listPos(target)
            return self.state[a][b]

    # assumes kings always exist, side = True if white, else black 
    def locateKing(self, isWhite: bool) -> str:
        if isWhite: king = 'K'
        else: king = 'k'
        temp = self.state
        for row in temp:
            if king in row:
                return self.chessPos(temp.index(row), row.index(king))
    
           
    def inCheck(self, isWhite: bool) -> bool:
        loc = self.locateKing(isWhite)
        return self.isSafe(isWhite, loc)

    def isMate(self, side: bool) -> bool:
        side = not side
        if not self.inCheck(side):
            return False
        if side:    clr = 1
        else:       clr = 2
        for i in _charRange('a','h'):
            for j in _charRange('1','8'):
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
        if self._repeatedMoves >= 50: return True
        if self.gameDraw: return True
        side = not side
        c = self.inCheck(side)
        if side:    clr = 1
        else:       clr = 2
        for i in _charRange('a','h'):
            for j in _charRange('1','8'):
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

    def _rookHelper(self, target: str) -> tuple[list[str], list[str]]:
        emptySquare = []
        attack = []
        for direction in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            current = self.look(target, direction)
            while self.colour(current) == 0:
                emptySquare.append(current)
                current = self.look(current, direction)
            if self.isEnemy(current, target): attack.append(current)
        return emptySquare, attack

    def _bishopHelper(self, target: str) -> tuple[list[str],list[str]]:
        emptySquare = []
        attack = []
        for direction in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
            current = self.look(target, direction)
            while self.colour(current) == 0:
                emptySquare.append(current)
                current = self.look(current, direction)
            if self.isEnemy(current, target): attack.append(current)
        return emptySquare, attack

    def _knightHelper(self, target: str) -> tuple[list[str], list[str]]:
        emptySquare = []
        attack = []
        for direction in permutations([-1,1,-2,2],2):
            if abs(direction[0]) != abs(direction[1]):
                move = self.look(target, direction)
                if (move != '00'):
                    if (self.colour(move) == 0):
                        emptySquare.append(move)
                    elif self.isEnemy(move, target):
                        attack.append(move)
        return emptySquare, attack

    def _kingHelper(self, target: str) -> tuple[list[str], list[str]]:
        isWhite = self.colour(target) == 1
        emptySquare = []
        attack = []

        for direction in (list(product([1,-1,0],[1,-1,0]))):
            if direction != (0,0):
                move = self.look(target, direction)
                if (move != '00'):
                    if (self.colour(move) == 0):
                        emptySquare.append(move)
                    elif self.isEnemy(move, target):
                        attack.append(move)

        # Castle check
        leftOne = self.look(target,(-1,0))
        rightOne = self.look(target,(1,0))
        leftTwo = self.look(target, (-2,0)) 
        rightTwo = self.look(target, (2,0))

        # KingHelper only considers castle moves on 'target' turn
        if self.whiteTurn == isWhite:
            danger = self.danger(isWhite)
            if target not in danger:
                if ((isWhite and self._whiteCastleLong) or (not isWhite and self._blackCastleLong)) and self.colour(leftOne) == 0 and self.colour(leftTwo) == 0 and (leftTwo not in danger) and (leftOne not in danger):
                    emptySquare.append(leftTwo)
                if ((isWhite and self._whiteCastle) or (not isWhite and self._blackCastle)) and self.colour(rightOne) == 0 and self.colour(rightTwo) == 0 and (rightTwo not in danger) and (rightOne not in danger):
                    emptySquare.append(rightTwo)


        return emptySquare, attack

    def _pawnHelper(self, target: str) -> tuple[list[str], list[str]]:
        emptySquare = []
        attack = []
        side = self.colour(target) == 1
        one = self.look(target, (0,1), side)   # 1 sqaure front of target
        two = self.look(target, (0,2), side)   # 2 squares front of target
        upright = self.look(target, (1,1), side)
        upleft = self.look(target, (-1,1), side)
        if self.name(one) == '0':
            emptySquare.append(one)
            if self.name(two) == '0':
                # When white pawn is on 7th row or black pawn is on 2nd row, they can move two squares
                if (target[1] == '2'  and self.name(target) == 'P') or (target[1] == '7' and self.name(target) == 'p'):
                    emptySquare.append(two)
        if self.isEnemy(upleft, target): attack.append(upleft)
        if self.isEnemy(upright,target): attack.append(upright)
        return emptySquare, attack

    # Input a position of a piece and return two list of all posible position
    def legal(self, target: str) -> tuple[list[str], list[str]]:
        piece = self.name(target)
        match piece:
            case 'P' | 'p':
                emptySquare, attack = self._pawnHelper(target)
            case 'R' | 'r':
                emptySquare, attack = self._rookHelper(target)
            case 'B' | 'b':
                emptySquare, attack = self._bishopHelper(target)
            case 'Q' | 'q':
                rookEmpty, rookAttack = self._rookHelper(target)
                bishopEmpty, bishopAttack = self._bishopHelper(target)
                emptySquare = rookEmpty + bishopEmpty
                attack = rookAttack + bishopAttack
            case 'N' | 'n':
                emptySquare, attack = self._knightHelper(target)
            case 'K' | 'k':
                emptySquare, attack = self._kingHelper(target)
        return emptySquare, attack

    def isSafe(self, side: bool, target: str) -> bool:
        return (target in self.danger(side))

    def danger(self, side: bool) -> list[str]:
        bad = []
        enemyColour = 1
        if side: enemyColour = 2
        for i in _charRange('a','h'):
            for j in _charRange('1','8'):
                k = i + j
                if self.colour(k) == enemyColour:
                    emptySquare, attack = self.legal(k)
                    bad = bad + emptySquare + attack
        list(set(bad))
        return bad

## TODO: add menu, add backtracks, stay on the same square after moving when flipping sides