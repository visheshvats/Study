package src.enums;

/**
 * Represents the two sides in chess.
 *
 * Design: Using an enum prevents invalid color values at compile time.
 * The opposite() method supports turn switching and piece-color checks.
 */
public enum Color {
    WHITE, BLACK;

    public Color opposite() {
        return this == WHITE ? BLACK : WHITE;
    }

    @Override
    public String toString() {
        return this == WHITE ? "White" : "Black";
    }
}
