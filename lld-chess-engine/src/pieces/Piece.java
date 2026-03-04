package src.pieces;

import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.List;

/**
 * Abstract base class for all chess pieces.
 *
 * Design decisions:
 * - STRATEGY PATTERN: Each piece encapsulates its own movement logic via
 * getValidMoves(). The Board/Game doesn't need switch statements —
 * it just calls piece.getValidMoves() polymorphically.
 * - FIRST MOVE TRACKING: Essential for pawn double-push, castling rights.
 * - FACTORY METHOD: PieceFactory creates pieces; this class just defines
 * behavior.
 *
 * Subclasses must implement:
 * - getPseudoLegalMoves(): All moves the piece could make ignoring check.
 * The Board filters these to find truly legal moves.
 */
public abstract class Piece {

    private final Color color;
    private final PieceType type;
    private boolean hasMoved;

    protected Piece(Color color, PieceType type) {
        this.color = color;
        this.type = type;
        this.hasMoved = false;
    }

    public Color getColor() {
        return color;
    }

    public PieceType getType() {
        return type;
    }

    public boolean hasMoved() {
        return hasMoved;
    }

    public void setMoved(boolean moved) {
        this.hasMoved = moved;
    }

    /**
     * Returns all pseudo-legal moves for this piece at the given position.
     * "Pseudo-legal" means the move follows the piece's movement rules
     * but doesn't account for check — the Board handles that filtering.
     *
     * @param position Current position of this piece
     * @param board    Read-only access to board state for collision checking
     */
    public abstract List<Position> getPseudoLegalMoves(Position position, src.board.Board board);

    /**
     * Returns the Unicode display symbol based on color.
     */
    public String getSymbol() {
        return type.getSymbol(color);
    }

    /**
     * Short identifier like "wK", "bP" for debugging.
     */
    public String getShortName() {
        String c = color == Color.WHITE ? "w" : "b";
        return c + type.getName().charAt(0);
    }

    @Override
    public String toString() {
        return color + " " + type.getName();
    }
}
