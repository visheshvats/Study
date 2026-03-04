package src.enums;

/**
 * All chess piece types with their display symbols and point values.
 *
 * Design decisions:
 * - UNICODE SYMBOLS: Rich console output for board printing.
 * - POINT VALUES: Standard chess values (P=1, N/B=3, R=5, Q=9, K=0).
 * King is 0 because it's invaluable — can't be captured.
 * - Each type maps to TWO symbols (white and black) for board display.
 */
public enum PieceType {
    KING("King", "♔", "♚", 0),
    QUEEN("Queen", "♕", "♛", 9),
    ROOK("Rook", "♖", "♜", 5),
    BISHOP("Bishop", "♗", "♝", 3),
    KNIGHT("Knight", "♘", "♞", 3),
    PAWN("Pawn", "♙", "♟", 1);

    private final String name;
    private final String whiteSymbol;
    private final String blackSymbol;
    private final int value;

    PieceType(String name, String whiteSymbol, String blackSymbol, int value) {
        this.name = name;
        this.whiteSymbol = whiteSymbol;
        this.blackSymbol = blackSymbol;
        this.value = value;
    }

    public String getName() {
        return name;
    }

    public String getWhiteSymbol() {
        return whiteSymbol;
    }

    public String getBlackSymbol() {
        return blackSymbol;
    }

    public int getValue() {
        return value;
    }

    public String getSymbol(Color color) {
        return color == Color.WHITE ? whiteSymbol : blackSymbol;
    }
}
