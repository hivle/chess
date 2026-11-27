# Colour constants
EMPTY = 0
WHITE = 1
BLACK = 2
OUT_OF_BOUNDS = 3

# Direction constants: (file_delta, rank_delta)
# Positive rank = toward rank 8 (white's forward), positive file = toward h-file
UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UP_LEFT = (-1, 1)
UP_RIGHT = (1, 1)
DOWN_LEFT = (-1, -1)
DOWN_RIGHT = (1, -1)

ROOK_DIRS = [UP, DOWN, LEFT, RIGHT]
BISHOP_DIRS = [UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]
ALL_DIRS = ROOK_DIRS + BISHOP_DIRS

KNIGHT_JUMPS = [
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    (1, -2), (1, 2), (2, -1), (2, 1)
]


# Lowercase for Black pieces, uppercase for White, 'N' is for knight
class Board:
    def __init__(self):
        self._whitePieces = ['R','N','B','Q','K','P']
        self._blackPieces = ['r','n','b','q','k','p']

        self.state: dict[str, bool | int] = {
            "whiteTurn": True,
            "whiteCastle": True,
            "blackCastle": True,
            "whiteCastleLong": True,
            "blackCastleLong": True,
            "repeatedMoves": 0
        }

        self.gameDraw = False

        self.board = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']]

        self.recording = True  # False on look-ahead copies: skip undo/log bookkeeping
        self.history = []      # board snapshots, for undo
        self.pastStates = []   # state dicts, for undo
        self.moveLog = []      # (start, end, notation) of every move played
        self.redoStack = []    # (start, end) of undone moves, for redo
        # Position keys for threefold repetition (board + turn + castling rights)
        self.positions = [self.positionKey()]

    def positionKey(self) -> str:
        """Identify a position for repetition: two positions are the same only
        if the pieces, side to move and castling rights all match. The
        en passant ghost 'X' is ignored."""
        s = self.state
        cells = ''.join(cell for row in self.board for cell in row).replace('X', '0')
        flags = ''.join('1' if s[k] else '0' for k in
                        ("whiteTurn", "whiteCastle", "whiteCastleLong", "blackCastle", "blackCastleLong"))
        return cells + flags

    def notation(self, start: str, end: str) -> str:
        """Readable move text, e.g. 'e2-e4', 'Ng1xf3', 'O-O', 'e7-e8=Q'."""
        piece = self.name(start)
        if piece in ('K', 'k') and abs(ord(end[0]) - ord(start[0])) == 2:
            return 'O-O' if end[0] == 'g' else 'O-O-O'
        isPawn = piece in ('P', 'p')
        capture = self.colour(end) != EMPTY or (isPawn and self.name(end) == 'X')
        text = ('' if isPawn else piece.upper()) + start + ('x' if capture else '-') + end
        if isPawn and end[1] in ('1', '8'):
            text += '=Q'
        return text

    def moveText(self) -> str:
        """The game so far, e.g. '1. e2-e4 e7-e5 2. Ng1-f3'."""
        parts = []
        for i, (_, _, text) in enumerate(self.moveLog):
            if i % 2 == 0:
                parts.append(f"{i // 2 + 1}.")
            parts.append(text)
        return ' '.join(parts)

    def __str__(self) -> str:
        result = ""
        for row in range(8, 0, -1):
            result += f"   ---------------------------------\n {row} | "
            for piece in self.board[8 - row]:
                result += f"{' ' if piece == '0' else piece} | "
            result += "\n"
        result += "   ---------------------------------\n    a   b   c   d   e   f   g   h\n"
        return result

    def isEnemy(self, squareOne: str, squareTwo: str) -> bool:
        pieceOne = self.name(squareOne)
        pieceTwo = self.name(squareTwo)
        # En passant marker counts as enemy only for pawns
        if pieceOne == 'X' or pieceTwo == 'X':
            return pieceOne in ('P', 'p') or pieceTwo in ('P', 'p')
        elif pieceOne in self._whitePieces:
            return pieceTwo in self._blackPieces
        elif pieceTwo in self._whitePieces:
            return pieceOne in self._blackPieces
        return False

    def listPos(self, square: str) -> tuple[int, int]:
        """Translate chess coordinates (e.g. 'e4') to board indexes (row, col)."""
        row = ord('8') - ord(square[1])
        col = ord(square[0]) - ord('a')
        return row, col

    def chessPos(self, row: int, col: int) -> str:
        """Translate board indexes (row, col) to chess coordinates (e.g. 'e4')."""
        return chr(ord('a') + col) + chr(ord('8') - row)

    def colour(self, target: str) -> int:
        """Return EMPTY, WHITE, BLACK, or OUT_OF_BOUNDS for a square."""
        val = self.name(target)
        if val in self._whitePieces:
            return WHITE
        elif val in self._blackPieces:
            return BLACK
        elif val in ('0', 'X'):
            return EMPTY
        return OUT_OF_BOUNDS

    def setValue(self, target: str, new: str):
        x, y = self.listPos(target)
        self.board[x][y] = new

    def copy(self) -> 'Board':
        """Cheap copy for trying out moves. Skips undo history, which
        look-ahead never needs and which grows every move."""
        b = object.__new__(Board)
        b._whitePieces = self._whitePieces
        b._blackPieces = self._blackPieces
        b.state = self.state.copy()
        b.gameDraw = self.gameDraw
        b.board = [row[:] for row in self.board]
        b.recording = False
        b.history = []
        b.pastStates = []
        b.moveLog = []
        b.redoStack = []
        b.positions = []
        return b

    @staticmethod
    def onBoard(square: str) -> bool:
        return len(square) == 2 and 'a' <= square[0] <= 'h' and '1' <= square[1] <= '8'

    def isLegal(self, start: str, end: str) -> bool:
        """True if start->end is a fully legal move for the side to move."""
        if not (self.onBoard(start) and self.onBoard(end)):
            return False
        if self.colour(start) != (WHITE if self.state["whiteTurn"] else BLACK):
            return False
        empty, attacks = self.legal(start)
        if end not in empty and end not in attacks:
            return False
        temp = self.copy()
        temp.move(start, end, False)
        return not temp.inCheck(self.state["whiteTurn"])

    def move(self, start: str, end: str, test: bool = True) -> bool:
        """Execute a move. If test=True, reject anything that isn't a legal move
        (wrong side, impossible for the piece, or leaves own king in check).
        test=False skips validation - for the AI and internal look-ahead,
        which only feed it moves from legal()."""
        if test and not self.isLegal(start, end):
            return False
        isWhite = self.colour(start) == WHITE

        # Save board state for undo, and log the move (real games only - the
        # AI's throwaway copies never undo, and this would slow the search)
        if self.recording:
            self.history.append(''.join(cell for row in self.board for cell in row))
            self.pastStates.append(self.state.copy())
            self.moveLog.append((start, end, self.notation(start, end)))
            self.redoStack.clear()  # a new move makes the undone moves unreachable

        self.state["repeatedMoves"] += 1
        if self.isEnemy(start, end):
            self.state["repeatedMoves"] = 0

        piece = self.name(start)

        # En passant capture: remove the pawn that was passed
        if piece in ('P', 'p') and self.name(end) == 'X':
            self.setValue(self.look(end, DOWN if isWhite else UP), '0')

        # Clear old en passant markers
        for i in range(8):
            if self.board[2][i] == 'X': self.board[2][i] = '0'
            if self.board[5][i] == 'X': self.board[5][i] = '0'

        if piece in ('P', 'p'):
            self.state["repeatedMoves"] = 0
            # Double push: mark the skipped square for en passant
            fwd = UP if isWhite else DOWN
            one = self.look(start, fwd)
            two = self.look(one, fwd)
            if end == two:
                self.setValue(one, 'X')

        elif piece == 'K':
            if self.state["whiteCastle"] and end == 'g1':
                self.setValue('f1', 'R')
                self.setValue('h1', '0')
            elif self.state["whiteCastleLong"] and end == 'c1':
                self.setValue('d1', 'R')
                self.setValue('a1', '0')

        elif piece == 'k':
            if self.state["blackCastle"] and end == 'g8':
                self.setValue('f8', 'r')
                self.setValue('h8', '0')
            elif self.state["blackCastleLong"] and end == 'c8':
                self.setValue('d8', 'r')
                self.setValue('a8', '0')

        # Move piece
        self.setValue(end, piece)
        self.setValue(start, '0')
        self.state["whiteTurn"] = not self.state["whiteTurn"]

        # Auto-promote pawns to queen
        for i in range(8):
            if self.board[0][i] == 'P': self.board[0][i] = 'Q'
            if self.board[7][i] == 'p': self.board[7][i] = 'q'

        # Revoke castling rights when king or rook moves, or a rook is captured
        if start in ('h1', 'e1') or end == 'h1': self.state["whiteCastle"] = False
        if start in ('a1', 'e1') or end == 'a1': self.state["whiteCastleLong"] = False
        if start in ('h8', 'e8') or end == 'h8': self.state["blackCastle"] = False
        if start in ('a8', 'e8') or end == 'a8': self.state["blackCastleLong"] = False

        # Threefold repetition: the same position (incl. turn and castling) a 3rd time
        if self.recording:
            key = self.positionKey()
            self.positions.append(key)
            if self.positions.count(key) >= 3:
                self.gameDraw = True

        return True

    def back(self) -> bool:
        """Undo the last move. It can be replayed with forward()."""
        if not self.history:
            return False
        last = self.history.pop()
        lastState = self.pastStates.pop()
        for i in range(8):
            for j in range(8):
                self.board[i][j] = last[i * 8 + j]
        self.state.update(lastState)
        if self.moveLog:
            start, end, _ = self.moveLog.pop()
            self.redoStack.append((start, end))
        if len(self.positions) > 1:
            self.positions.pop()
        # Undoing past a repetition clears the draw
        self.gameDraw = any(self.positions.count(p) >= 3 for p in set(self.positions))
        return True

    def forward(self) -> bool:
        """Redo the last undone move."""
        if not self.redoStack:
            return False
        start, end = self.redoStack.pop()
        remaining = self.redoStack[:]
        self.move(start, end, False)  # it was legal when first played
        self.redoStack = remaining    # move() clears redo; keep the rest
        return True

    def look(self, target: str, direction: tuple[int, int]) -> str:
        """Return the square in 'direction' from target, or '00' if off-board."""
        letter = chr(ord(target[0]) + direction[0])
        number = chr(ord(target[1]) + direction[1])
        if 'a' <= letter <= 'h' and '1' <= number <= '8':
            return letter + number
        return '00'

    def name(self, target: str) -> str:
        """Return the piece at target, or 'W' if out of bounds."""
        if 'a' <= target[0] <= 'h' and '1' <= target[1] <= '8':
            a, b = self.listPos(target)
            return self.board[a][b]
        return 'W'

    def locateKing(self, isWhite: bool) -> str:
        king = 'K' if isWhite else 'k'
        for r, row in enumerate(self.board):
            if king in row:
                return self.chessPos(r, row.index(king))

    def inCheck(self, isWhite: bool) -> bool:
        return self.isAttacked(isWhite, self.locateKing(isWhite))

    def isMate(self, whiteToMove: bool) -> bool:
        if not self.inCheck(whiteToMove):
            return False
        return not self._hasLegalMove(whiteToMove)

    def isDraw(self, whiteToMove: bool) -> bool:
        # Fifty-move rule: 50 full moves = 100 half-moves without capture or pawn move
        if self.state["repeatedMoves"] >= 100: return True
        if self.gameDraw: return True
        if self.inCheck(whiteToMove):
            return False
        return not self._hasLegalMove(whiteToMove)

    def _hasLegalMove(self, whiteToMove: bool) -> bool:
        clr = WHITE if whiteToMove else BLACK
        for r in range(8):
            for c in range(8):
                sq = self.chessPos(r, c)
                if self.colour(sq) == clr:
                    moves, attacks = self.legal(sq)
                    for target in moves + attacks:
                        temp = self.copy()
                        temp.move(sq, target, False)
                        if not temp.inCheck(whiteToMove):
                            return True
        return False

    def _slidingMoves(self, target: str, directions: list) -> tuple[list[str], list[str]]:
        """Shared logic for rook, bishop, and queen."""
        emptySquares = []
        attacks = []
        for d in directions:
            current = self.look(target, d)
            while self.colour(current) == EMPTY:
                emptySquares.append(current)
                current = self.look(current, d)
            if self.isEnemy(current, target):
                attacks.append(current)
        return emptySquares, attacks

    def _knightHelper(self, target: str) -> tuple[list[str], list[str]]:
        emptySquares = []
        attacks = []
        for jump in KNIGHT_JUMPS:
            sq = self.look(target, jump)
            if sq != '00':
                if self.colour(sq) == EMPTY:
                    emptySquares.append(sq)
                elif self.isEnemy(sq, target):
                    attacks.append(sq)
        return emptySquares, attacks

    def _kingHelper(self, target: str) -> tuple[list[str], list[str]]:
        isWhite = self.colour(target) == WHITE
        emptySquares = []
        attacks = []

        for d in ALL_DIRS:
            sq = self.look(target, d)
            if sq != '00':
                if self.colour(sq) == EMPTY:
                    emptySquares.append(sq)
                elif self.isEnemy(sq, target):
                    attacks.append(sq)

        # Castling (only on this king's turn, from its home square, with the rook still home)
        if self.state["whiteTurn"] == isWhite and target == ('e1' if isWhite else 'e8'):
            danger = self.danger(isWhite)
            rook = 'R' if isWhite else 'r'
            if target not in danger:
                # Queenside
                d1 = self.look(target, LEFT)
                c1 = self.look(target, (-2, 0))
                b1 = self.look(target, (-3, 0))
                canLong = (isWhite and self.state["whiteCastleLong"]) or (not isWhite and self.state["blackCastleLong"])
                if canLong and self.name(self.look(target, (-4, 0))) == rook \
                        and self.colour(d1) == EMPTY and self.colour(c1) == EMPTY and self.colour(b1) == EMPTY:
                    if d1 not in danger and c1 not in danger:
                        emptySquares.append(c1)
                # Kingside
                f1 = self.look(target, RIGHT)
                g1 = self.look(target, (2, 0))
                canShort = (isWhite and self.state["whiteCastle"]) or (not isWhite and self.state["blackCastle"])
                if canShort and self.name(self.look(target, (3, 0))) == rook \
                        and self.colour(f1) == EMPTY and self.colour(g1) == EMPTY:
                    if f1 not in danger and g1 not in danger:
                        emptySquares.append(g1)

        return emptySquares, attacks

    def _pawnHelper(self, target: str) -> tuple[list[str], list[str]]:
        emptySquares = []
        attacks = []
        isWhite = self.colour(target) == WHITE
        fwd = UP if isWhite else DOWN
        startRank = '2' if isWhite else '7'

        one = self.look(target, fwd)
        if self.name(one) == '0':
            emptySquares.append(one)
            two = self.look(one, fwd)
            if target[1] == startRank and self.name(two) == '0':
                emptySquares.append(two)

        # Diagonal captures (including en passant)
        for side_dir in (UP_LEFT, UP_RIGHT) if isWhite else (DOWN_LEFT, DOWN_RIGHT):
            diag = self.look(target, side_dir)
            if self.isEnemy(diag, target):
                attacks.append(diag)

        return emptySquares, attacks

    def legal(self, target: str) -> tuple[list[str], list[str]]:
        """Return pseudo-legal moves (may leave king in check)."""
        piece = self.name(target)
        match piece:
            case 'P' | 'p': return self._pawnHelper(target)
            case 'R' | 'r': return self._slidingMoves(target, ROOK_DIRS)
            case 'B' | 'b': return self._slidingMoves(target, BISHOP_DIRS)
            case 'Q' | 'q': return self._slidingMoves(target, ALL_DIRS)
            case 'N' | 'n': return self._knightHelper(target)
            case 'K' | 'k': return self._kingHelper(target)
            case _:         return [], []

    def legalFiltered(self, target: str) -> tuple[list[str], list[str]]:
        """Return only truly legal moves (excludes moves that leave king in check)."""
        isWhite = self.colour(target) == WHITE
        emptySquares, attacks = self.legal(target)
        def safe(sq):
            temp = self.copy()
            temp.move(target, sq, False)
            return not temp.inCheck(isWhite)
        return [sq for sq in emptySquares if safe(sq)], [sq for sq in attacks if safe(sq)]

    def isAttacked(self, side: bool, target: str) -> bool:
        """Return True if target square is attacked by the opponent of 'side'."""
        return target in self.danger(side)

    def danger(self, side: bool) -> list[str]:
        """Return list of squares attacked by the opponent of 'side'.

        Uses simplified attack patterns: pawns only attack diagonally,
        kings use basic moves (no castling), to avoid recursion.
        """
        bad = set()
        enemyColour = BLACK if side else WHITE
        for r in range(8):
            for c in range(8):
                sq = self.chessPos(r, c)
                if self.colour(sq) != enemyColour:
                    continue
                piece = self.name(sq)
                if piece in ('P', 'p'):
                    isWhite = piece == 'P'
                    for d in ((UP_LEFT, UP_RIGHT) if isWhite else (DOWN_LEFT, DOWN_RIGHT)):
                        diag = self.look(sq, d)
                        if diag != '00':
                            bad.add(diag)
                elif piece in ('K', 'k'):
                    for d in ALL_DIRS:
                        adj = self.look(sq, d)
                        if adj != '00':
                            bad.add(adj)
                else:
                    moves, attacks = self.legal(sq)
                    bad.update(moves)
                    bad.update(attacks)
        return list(bad)
