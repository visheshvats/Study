package src;

/**
 * Encapsulates the 3x3 (or NxN) grid and all board-related operations.
 *
 * Design principles applied:
 * 1. Single Responsibility: Board knows nothing about players or game rules.
 * It just manages a 2D array of Cells. This makes it reusable for other
 * grid-based games (Connect Four, Battleship, etc.)
 * 2. Composition: Board OWNS its Cells. When Board is created, all Cells
 * are created. When Board is GC'd, Cells go with it.
 * 3. Encapsulation: The grid array is private. External code accesses cells
 * through getCell(), which validates bounds first.
 * 4. Validation centralized: validatePosition() is called by every public
 * method that takes coordinates — no duplication.
 */
public class Board {

    private final Cell[][] grid;
    private final int size;

    public Board(int size) {
        this.size = size;
        this.grid = new Cell[size][size];
        initializeBoard();
    }

    // Creates all Cell objects so we never have null cells
    private void initializeBoard() {
        for (int r = 0; r < size; r++) {
            for (int c = 0; c < size; c++) {
                grid[r][c] = new Cell();
            }
        }
    }

    public int getSize() {
        return size;
    }

    /**
     * Returns the Cell at the given position after bounds validation.
     */
    public Cell getCell(int row, int col) {
        validatePosition(row, col);
        return grid[row][col];
    }

    /**
     * Places a symbol on the board. Does NOT check if the cell is empty —
     * that responsibility belongs to the Game class.
     */
    public void placeSymbol(int row, int col, Symbol symbol) {
        validatePosition(row, col);
        grid[row][col].setSymbol(symbol);
    }

    /**
     * Returns true if the cell at (row, col) is empty.
     */
    public boolean isCellEmpty(int row, int col) {
        validatePosition(row, col);
        return grid[row][col].isEmpty();
    }

    /**
     * Returns true if every cell on the board is filled.
     * Short-circuits as soon as an empty cell is found.
     */
    public boolean isFull() {
        for (int r = 0; r < size; r++) {
            for (int c = 0; c < size; c++) {
                if (grid[r][c].isEmpty()) {
                    return false; // Short-circuit
                }
            }
        }
        return true;
    }

    /**
     * Prints the current board state to the console.
     * In a real app, this would be in a separate View layer.
     */
    public void printBoard() {
        System.out.println();
        // Column indices header
        System.out.print("  ");
        for (int c = 0; c < size; c++) {
            System.out.print(c + " ");
        }
        System.out.println();

        for (int r = 0; r < size; r++) {
            System.out.print(r + " ");
            for (int c = 0; c < size; c++) {
                System.out.print(grid[r][c].getSymbol().getDisplayChar() + " ");
            }
            System.out.println();
        }
        System.out.println();
    }

    // Private validation — called by all public methods that take coordinates
    private void validatePosition(int row, int col) {
        if (row < 0 || row >= size || col < 0 || col >= size) {
            throw new InvalidMoveException(
                    "Position (" + row + ", " + col + ") is out of bounds for a " + size + "x" + size + " board.");
        }
    }
}
