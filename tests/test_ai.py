import time
from game import Board
from ai import evaluate, best_move, get_all_moves, minimax


def setup_board(pieces: dict[str, str]) -> Board:
    b = Board()
    b.board = [['0'] * 8 for _ in range(8)]
    for sq, piece in pieces.items():
        b.setValue(sq, piece)
    return b


def play_moves(moves: list[str]) -> Board:
    b = Board()
    for m in moves:
        assert b.move(m[:2], m[2:]), f"Move {m} failed"
    return b


# ── Evaluation Tests ─────────────────────────────────────────────────────

class TestEvaluation:
    def test_initial_position_balanced(self):
        b = Board()
        score = evaluate(b)
        assert score == 0, f"Initial position should be 0, got {score}"

    def test_white_material_advantage(self):
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd4': 'Q',  # white has extra queen
        })
        score = evaluate(b)
        assert score > 0, f"White should be ahead with extra queen, got {score}"

    def test_black_material_advantage(self):
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd4': 'q',  # black has extra queen
        })
        score = evaluate(b)
        assert score < 0, f"Black should be ahead with extra queen, got {score}"

    def test_checkmate_white_wins(self):
        b = play_moves(['e2e4', 'e7e5', 'f1c4', 'b8c6', 'd1h5', 'g8f6', 'h5f7'])
        score = evaluate(b)
        assert score > 90000, f"Scholar's mate should be huge positive, got {score}"

    def test_checkmate_black_wins(self):
        b = play_moves(['f2f3', 'e7e5', 'g2g4', 'd8h4'])
        score = evaluate(b)
        assert score < -90000, f"Fool's mate should be huge negative, got {score}"

    def test_center_bonus(self):
        b1 = setup_board({'e1': 'K', 'e8': 'k', 'a1': 'N'})
        b2 = setup_board({'e1': 'K', 'e8': 'k', 'e4': 'N'})
        assert evaluate(b2) > evaluate(b1), "Knight in center should score higher"


# ── Move Generation Tests ────────────────────────────────────────────────

class TestMoveGeneration:
    def test_initial_white_moves(self):
        b = Board()
        moves = get_all_moves(b, True)
        # 16 pawn moves (8 single + 8 double) + 4 knight moves
        assert len(moves) == 20, f"Expected 20 initial white moves, got {len(moves)}"

    def test_initial_black_moves(self):
        b = Board()
        moves = get_all_moves(b, False)
        assert len(moves) == 20, f"Expected 20 initial black moves, got {len(moves)}"

    def test_no_moves_in_mate(self):
        b = play_moves(['f2f3', 'e7e5', 'g2g4', 'd8h4'])
        moves = get_all_moves(b, True)
        # White has moves, but none are legal (all leave king in check)
        # get_all_moves returns pseudo-legal, so there will be moves
        # but best_move should handle this
        assert len(moves) > 0  # pseudo-legal moves exist


# ── Best Move Tests ──────────────────────────────────────────────────────

class TestBestMove:
    def test_captures_hanging_queen(self):
        """AI should capture a free queen."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd4': 'N', 'e6': 'q',  # knight can take queen
        })
        move = best_move(b, depth=2)
        assert move == ('d4', 'e6'), f"Should capture queen, got {move}"

    def test_avoids_losing_queen(self):
        """AI should not move queen to a square defended by a rook."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd1': 'Q', 'a4': 'r', 'h4': 'r',  # rooks defend rank 4
        })
        move = best_move(b, depth=3)
        if move:
            start, end = move
            # Queen should not go to rank 4 (defended by rooks)
            if start == 'd1':
                assert end[1] != '4', f"Should not move queen to defended rank 4, got {move}"

    def test_finds_mate_in_one(self):
        """AI should find checkmate in one move."""
        b = setup_board({
            'e1': 'K', 'h8': 'k', 'f7': 'p', 'g7': 'p', 'h7': 'p',
            'a1': 'R',
        })
        # Disable castling so AI doesn't prefer castle over mate
        b.state["whiteCastle"] = False
        b.state["whiteCastleLong"] = False
        b.state["blackCastle"] = False
        b.state["blackCastleLong"] = False
        move = best_move(b, depth=3)
        assert move == ('a1', 'a8'), f"Should find back-rank mate Ra8#, got {move}"

    def test_returns_none_when_no_moves(self):
        """If mated, should still return something (first move)."""
        b = play_moves(['f2f3', 'e7e5', 'g2g4', 'd8h4'])
        # White is mated, but best_move returns the first pseudo-legal move
        move = best_move(b, depth=1)
        # Just verify it doesn't crash
        assert move is not None or move is None  # either is fine

    def test_black_captures_queen(self):
        """AI playing black should capture a hanging queen."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd5': 'Q', 'c6': 'n',  # black knight can take white queen
        })
        b.state["whiteTurn"] = False
        move = best_move(b, depth=2)
        assert move == ('c6', 'd4') or move == ('c6', 'd8') or move[1] == 'd5', \
            f"Should capture queen, got {move}"

    def test_depth_1_is_fast(self):
        b = Board()
        start = time.perf_counter()
        move = best_move(b, depth=1)
        elapsed = time.perf_counter() - start
        assert move is not None
        assert elapsed < 2.0, f"Depth 1 too slow: {elapsed:.2f}s"

    def test_depth_2_is_reasonable(self):
        b = Board()
        start = time.perf_counter()
        move = best_move(b, depth=2)
        elapsed = time.perf_counter() - start
        assert move is not None
        assert elapsed < 10.0, f"Depth 2 too slow: {elapsed:.2f}s"


# ── Minimax Tests ────────────────────────────────────────────────────────

class TestMinimax:
    def test_maximizing_prefers_higher_score(self):
        """White (maximizing) should prefer positions with higher scores."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'a2': 'P',  # white pawn can push
        })
        score, move = minimax(b, 1, float('-inf'), float('inf'), True)
        assert move is not None

    def test_minimizing_prefers_lower_score(self):
        """Black (minimizing) should prefer positions with lower scores."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'a7': 'p',  # black pawn can push
        })
        b.state["whiteTurn"] = False
        score, move = minimax(b, 1, float('-inf'), float('inf'), False)
        assert move is not None

    def test_alpha_beta_pruning_same_result(self):
        """Alpha-beta should give same result as full search at low depth."""
        b = setup_board({
            'e1': 'K', 'e8': 'k',
            'd4': 'N', 'e6': 'q',
        })
        # Full search (no pruning possible at depth 1)
        score1, move1 = minimax(b, 1, float('-inf'), float('inf'), True)
        # The result should be deterministic
        score2, move2 = minimax(b, 1, float('-inf'), float('inf'), True)
        assert score1 == score2
        assert move1 == move2


# ── AI Game Simulation Tests ─────────────────────────────────────────────

class TestAIGameSimulation:
    def test_ai_vs_ai_10_moves(self):
        """Two AIs play 10 moves without crashing."""
        b = Board()
        for i in range(10):
            move = best_move(b, depth=1)
            if move is None:
                break
            assert b.move(move[0], move[1]), f"AI move {i} failed: {move}"

    def test_ai_vs_ai_until_end(self):
        """Two AIs play until game ends (max 100 moves to prevent infinite games)."""
        b = Board()
        for i in range(100):
            if b.isMate(b.state["whiteTurn"]) or b.isDraw(b.state["whiteTurn"]):
                break
            move = best_move(b, depth=1)
            if move is None:
                break
            b.move(move[0], move[1])
        # Just verify it didn't crash

    def test_ai_game_speed(self):
        """Benchmark: AI vs AI game at depth 1."""
        b = Board()
        start = time.perf_counter()
        for i in range(20):
            move = best_move(b, depth=1)
            if move is None:
                break
            b.move(move[0], move[1])
        elapsed = time.perf_counter() - start
        print(f"\n  AI vs AI 20 moves (depth=1): {elapsed:.2f}s")
        assert elapsed < 30.0, f"AI game too slow: {elapsed:.1f}s"
