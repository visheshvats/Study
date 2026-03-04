package src;

/**
 * Checks if all cells in the row of the last move contain the same symbol.
 *
 * We only check the row where the last move was made — not all rows.
 * This is an optimization: a win can only occur in the row just played.
 */
public class RowWinningStrategy implements WinningStrategy {

    @Override
    public boolean checkWin(Board board, int row, int col, Symbol symbol) {
        for (int c = 0; c < board.getSize(); c++) {
            if (board.getCell(row, c).getSymbol() != symbol) {
                return false; // Short-circuit: no need to check further
            }
        }
        return true;
    }
}
