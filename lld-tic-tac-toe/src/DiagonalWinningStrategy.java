package src;

/**
 * Checks both diagonals for a win.
 *
 * Two diagonals exist:
 * - Main diagonal: (0,0), (1,1), (2,2) → row == col
 * - Anti-diagonal: (0,2), (1,1), (2,0) → row + col == size - 1
 *
 * Key insight: "size - 1 - i" gives the anti-diagonal column index.
 * For a 3x3 board: i=0 → col=2, i=1 → col=1, i=2 → col=0
 */
public class DiagonalWinningStrategy implements WinningStrategy {

    @Override
    public boolean checkWin(Board board, int row, int col, Symbol symbol) {
        int size = board.getSize();

        // Check main diagonal (top-left to bottom-right)
        boolean mainDiagonalWin = true;
        for (int i = 0; i < size; i++) {
            if (board.getCell(i, i).getSymbol() != symbol) {
                mainDiagonalWin = false;
                break;
            }
        }

        // Check anti-diagonal (top-right to bottom-left)
        boolean antiDiagonalWin = true;
        for (int i = 0; i < size; i++) {
            if (board.getCell(i, size - 1 - i).getSymbol() != symbol) {
                antiDiagonalWin = false;
                break;
            }
        }

        return mainDiagonalWin || antiDiagonalWin;
    }
}
