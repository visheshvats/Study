package src;

/**
 * Strategy Pattern — Win Detection Interface.
 *
 * Each implementation checks one way to win (row, column, diagonal).
 * Adding a new win condition (e.g., for a 4x4 board) means adding
 * a new class — no changes to existing code (Open/Closed Principle).
 *
 * Parameters:
 * 
 * @param board  The current board state
 * @param row    Row of the last move
 * @param col    Column of the last move
 * @param symbol The symbol that just moved
 */
public interface WinningStrategy {
    boolean checkWin(Board board, int row, int col, Symbol symbol);
}
