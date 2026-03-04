package src.pieces;

import src.enums.Color;
import src.enums.PieceType;

/**
 * Factory Pattern — Creates pieces by type and color.
 *
 * Why a Factory?
 * 1. Centralizes piece creation — changes to constructor signatures
 * only affect this one class.
 * 2. Supports FEN parsing — given a character like 'K', 'p', 'N',
 * the factory determines the correct piece type and color.
 * 3. Eliminates switch/if chains in client code.
 *
 * Example:
 * Piece queen = PieceFactory.create(PieceType.QUEEN, Color.WHITE);
 * Piece fromFen = PieceFactory.fromFenChar('n'); // Black Knight
 */
public final class PieceFactory {

    private PieceFactory() {
    } // utility class

    /**
     * Creates a piece of the given type and color.
     */
    public static Piece create(PieceType type, Color color) {
        return switch (type) {
            case KING -> new King(color);
            case QUEEN -> new Queen(color);
            case ROOK -> new Rook(color);
            case BISHOP -> new Bishop(color);
            case KNIGHT -> new Knight(color);
            case PAWN -> new Pawn(color);
        };
    }

    /**
     * Creates a piece from a FEN character.
     * Uppercase = White, lowercase = Black.
     * K/k=King, Q/q=Queen, R/r=Rook, B/b=Bishop, N/n=Knight, P/p=Pawn
     */
    public static Piece fromFenChar(char c) {
        Color color = Character.isUpperCase(c) ? Color.WHITE : Color.BLACK;
        char upper = Character.toUpperCase(c);

        PieceType type = switch (upper) {
            case 'K' -> PieceType.KING;
            case 'Q' -> PieceType.QUEEN;
            case 'R' -> PieceType.ROOK;
            case 'B' -> PieceType.BISHOP;
            case 'N' -> PieceType.KNIGHT;
            case 'P' -> PieceType.PAWN;
            default -> throw new IllegalArgumentException("Unknown FEN char: " + c);
        };

        return create(type, color);
    }

    /**
     * Returns the FEN character for a piece.
     */
    public static char toFenChar(Piece piece) {
        char c = switch (piece.getType()) {
            case KING -> 'K';
            case QUEEN -> 'Q';
            case ROOK -> 'R';
            case BISHOP -> 'B';
            case KNIGHT -> 'N';
            case PAWN -> 'P';
        };
        return piece.getColor() == Color.WHITE ? c : Character.toLowerCase(c);
    }
}
