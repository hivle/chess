from game import board

class play:
    def __init__(self, side: bool = True):
        self.new = board()
        if (side): self.new.print_board()
        else: self.new.print_board(False)

    def move(self, m: str) -> bool:
        if not ('a' <= m[0] <= 'h' and 'a' <= m[2] <= 'h' and len(m) == 4 and '1' <= m[1] <= '8' and '1' <= m[3] <='8'):
            return False
        start = m[0] + m[1]
        end = m[2] + m[3]
        return self.new.move(start, end)
    
    def print_board(self, side: bool = True):
        self.new.print_board(side)


def main():
    g1 = play()
    while True:
        print(g1.new.locateKing(True))
        print(g1.new.danger(True))
        print(g1.new.inCheck(True))
        print(g1.new.isMate(True))
        m = input("move: ")
        if m == "end": exit()
        if not (g1.move(m)):
            g1.print_board()
            print("ilegal move")
        else:
            g1.print_board()


if __name__ == "__main__":
    main()
