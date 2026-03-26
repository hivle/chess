#!/usr/bin/env python3
"""Play chess in the terminal — no pygame required."""

from game import Board
from ai import best_move


def main():
    print("=== Chess CLI ===")
    print("Enter moves as: e2e4")
    print("Commands: undo, quit\n")

    # Choose mode
    print("1) 2 Player")
    print("2) AI Easy")
    print("3) AI Medium")
    print("4) AI Hard")
    choice = input("Select mode [1-4]: ").strip()
    ai_depth = {'2': 1, '3': 2, '4': 3}.get(choice, 0)

    board = Board()

    while True:
        print(board)
        turn = "White" if board.state["whiteTurn"] else "Black"

        if board.isMate(board.state["whiteTurn"]):
            winner = "Black" if board.state["whiteTurn"] else "White"
            print(f"Checkmate! {winner} wins!")
            break
        if board.isDraw(board.state["whiteTurn"]):
            print("Draw!")
            break

        if board.inCheck(board.state["whiteTurn"]):
            print(f"  {turn} is in check!")

        # AI turn
        if ai_depth > 0 and not board.state["whiteTurn"]:
            print(f"  {turn} (AI) is thinking...")
            move = best_move(board, ai_depth)
            if move is None:
                print("AI has no moves.")
                break
            print(f"  AI plays: {move[0]}{move[1]}")
            board.move(move[0], move[1])
            continue

        # Human turn
        cmd = input(f"  {turn} move: ").strip().lower()
        if cmd == "quit":
            break
        if cmd == "undo":
            board.back()
            if ai_depth > 0:
                board.back()  # undo AI move too
            continue
        if len(cmd) != 4:
            print("  Invalid. Use format like e2e4")
            continue

        start, end = cmd[:2], cmd[2:]
        if not board.move(start, end):
            print("  Illegal move, try again.")


if __name__ == "__main__":
    main()
