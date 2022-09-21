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
    
    def print_board(self):
        for i in self.state:
            print('---------------------------------\n| ', end = '')
            for j in i:
                if j == '0':
                    print(' ', end = ' | ')
                else:
                    print (j, end = ' | ')
            print('') # prints new line after each row
    
    # def side(self, pos):
    #     if self.state  = 
    # # Input a position of a piece and return all legal moves for that piece
    # def legal(self, position):

def main():
    new = board()
    new.print_board()


if __name__ == "__main__":
    main()
