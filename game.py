class square:
    def __init__(self, pos: str):
        try:
            assert (len(pos) == 2 and
                    'a' <= pos[0] <= 'h' and
                    '1' <= pos[1] <= '8'), "Error: Position not allowed, Chess position must be in the range 'a1' to 'h8'"
        except Exception as e:
            print(e)
            return None
        else:
            self.row = ord(pos[1]) - ord('8')
            self.col = ord(pos[0]) - ord('a')
    
    def target(self) -> tuple[int,int]:
         return (self.row, self.col)

# Lowercase for Black pieces, uppercase for White, 'N' is for knight
class board:
    def __init__(self):
        self.state = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0'],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']]
    
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
    
    # returns 0 for empty, 1 for white, 2 for black
    def colourCode(self, pos: square) -> int:
        col, row = pos.target()
        val = self.state[row][col]
        if val == '0':
            return 0
        elif val.isupper(): return 1
        else: return 2

    # Input a position of a piece and return all legal moves for that piece
    # def legal(self, position):

def main():
    new = board()
    new.print_board()
    sq = square('a2')
    sq2 = square('a29')
    print (sq)
    print (sq2)
    #print(board.colourCode('a1'))
    del new

if __name__ == "__main__":
    main()
