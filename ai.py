"""Simple chess AI using minimax with alpha-beta pruning."""

from copy import deepcopy
from game import Board, WHITE, BLACK

# Piece values for evaluation
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': 0,
    '0': 0, 'X': 0,
}

# Bonus for pieces being in the center
CENTER_SQUARES = {'d4', 'e4', 'd5', 'e5'}
EXTENDED_CENTER = {'c3', 'd3', 'e3', 'f3', 'c4', 'f4', 'c5', 'f5', 'c6', 'd6', 'e6', 'f6'}


def evaluate(board: Board) -> float:
    """Evaluate the board position. Positive = white advantage, negative = black."""
    if board.isMate(True): return -99999
    if board.isMate(False): return 99999
    if board.isDraw(True) or board.isDraw(False): return 0

    score = 0

    for r in range(8):
        for c in range(8):
            piece = board.board[r][c]
            score += PIECE_VALUES.get(piece, 0)

            sq = board.chessPos(r, c)
            if piece != '0' and piece != 'X':
                # Small bonus for center control
                if sq in CENTER_SQUARES:
                    score += 10 if piece.isupper() else -10
                elif sq in EXTENDED_CENTER:
                    score += 5 if piece.isupper() else -5

    return score


def get_all_moves(board: Board, whiteToMove: bool) -> list[tuple[str, str]]:
    """Return all legal moves for the given side as (start, end) pairs."""
    clr = WHITE if whiteToMove else BLACK
    moves = []
    for r in range(8):
        for c in range(8):
            sq = board.chessPos(r, c)
            if board.colour(sq) == clr:
                empty, attacks = board.legal(sq)
                for target in attacks + empty:  # check captures first for better pruning
                    moves.append((sq, target))
    return moves


def minimax(board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> tuple[float, tuple[str, str] | None]:
    """Minimax with alpha-beta pruning.

    Returns (score, best_move) where best_move is (start, end) or None.
    """
    whiteToMove = board.state["whiteTurn"]

    if depth == 0:
        return evaluate(board), None

    moves = get_all_moves(board, whiteToMove)
    if not moves:
        if board.inCheck(whiteToMove):
            return (-99999 if whiteToMove else 99999), None
        return 0, None  # stalemate

    best_move = None
    found_legal = False

    if maximizing:
        max_eval = float('-inf')
        for start, end in moves:
            temp = deepcopy(board)
            if not temp.move(start, end, False):
                continue
            if temp.inCheck(whiteToMove):
                continue
            found_legal = True
            score, _ = minimax(temp, depth - 1, alpha, beta, False)
            if score > max_eval:
                max_eval = score
                best_move = (start, end)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        if not found_legal:
            if board.inCheck(whiteToMove):
                return -99999, None
            return 0, None
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for start, end in moves:
            temp = deepcopy(board)
            if not temp.move(start, end, False):
                continue
            if temp.inCheck(whiteToMove):
                continue
            found_legal = True
            score, _ = minimax(temp, depth - 1, alpha, beta, True)
            if score < min_eval:
                min_eval = score
                best_move = (start, end)
            beta = min(beta, score)
            if beta <= alpha:
                break
        if not found_legal:
            if board.inCheck(whiteToMove):
                return 99999, None
            return 0, None
        return min_eval, best_move


def best_move(board: Board, depth: int = 3) -> tuple[str, str] | None:
    """Find the best move for the current side using minimax.

    Args:
        board: Current board state.
        depth: Search depth (higher = stronger but slower). Default 3.

    Returns:
        (start, end) tuple, or None if no legal moves.
    """
    maximizing = board.state["whiteTurn"]
    score, move = minimax(board, depth, float('-inf'), float('inf'), maximizing)
    return move
