package src;

/**
 * Checks if all cells in the column of the last move contain the same symbol.
 *
 * Mirror of RowWinningStrategy — iterates through rows instead of columns.
 * Each strategy is independently testable without a full Game setup.
 */
public class ColumnWinningStrategy implements WinningStrategy {

    @Override
    public boolean checkWin(Board board, int row, int col, Symbol symbol) {
        for (int r = 0; r < board.getSize(); r++) {
            if (board.getCell(r, col).getSymbol() != symbol) {
                return false; // Short-circuit
            }
        }
        return true;
    }
}
