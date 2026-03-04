package src.core;

/**
 * Immutable value object representing a position on the chess board.
 *
 * Design decisions:
 * - IMMUTABLE: Positions never change — a new Position is created instead.
 * This prevents bugs where a shared position is accidentally mutated.
 * - ALGEBRAIC NOTATION: Supports conversion to/from "e4", "a1", etc.
 * - ZERO-INDEXED: Internal representation uses 0-7 for rows and columns.
 * Row 0 = rank 1 (White's back rank), Row 7 = rank 8 (Black's back rank).
 * - isValid(): Bounds-checking to prevent ArrayIndexOutOfBoundsException.
 */
public class Position {

    private final int row; // 0-7 (rank 1-8)
    private final int col; // 0-7 (file a-h)

    public Position(int row, int col) {
        this.row = row;
        this.col = col;
    }

    /**
     * Creates a Position from algebraic notation like "e4".
     * 'e' → col 4, '4' → row 3 (zero-indexed)
     */
    public static Position fromAlgebraic(String notation) {
        if (notation == null || notation.length() != 2) {
            throw new IllegalArgumentException("Invalid notation: " + notation);
        }
        int col = notation.charAt(0) - 'a';
        int row = notation.charAt(1) - '1';
        Position pos = new Position(row, col);
        if (!pos.isValid()) {
            throw new IllegalArgumentException("Out of bounds: " + notation);
        }
        return pos;
    }

    /**
     * Converts to algebraic notation: "e4", "a1", etc.
     */
    public String toAlgebraic() {
        return "" + (char) ('a' + col) + (char) ('1' + row);
    }

    public int getRow() {
        return row;
    }

    public int getCol() {
        return col;
    }

    /**
     * Returns true if this position is within the 8×8 board.
     */
    public boolean isValid() {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }

    /**
     * Returns a new Position offset by (dRow, dCol).
     * Does NOT validate — caller must check isValid().
     */
    public Position offset(int dRow, int dCol) {
        return new Position(row + dRow, col + dCol);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (!(o instanceof Position))
            return false;
        Position p = (Position) o;
        return row == p.row && col == p.col;
    }

    @Override
    public int hashCode() {
        return 31 * row + col;
    }

    @Override
    public String toString() {
        return toAlgebraic();
    }
}
