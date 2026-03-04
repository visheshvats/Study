package src.core;

import src.enums.PieceType;
import src.pieces.Piece;

/**
 * Represents a single move in a chess game.
 *
 * Design decisions:
 * - IMMUTABLE: Once created, a Move cannot change. This is essential for
 * the Command pattern (undo/redo) — we need to reconstruct previous state.
 * - CAPTURES: Stores the captured piece for undo support.
 * - SPECIAL MOVES: Flags for castling, en passant, and promotion.
 * - ALGEBRAIC NOTATION: toString() produces human-readable "e2→e4" format.
 *
 * Command Pattern: Each Move acts as a command object that can be executed
 * (apply to board) and undone (restore previous state).
 */
public class Move {

    private final Position from;
    private final Position to;
    private final Piece movedPiece;
    private final Piece capturedPiece; // null if no capture
    private final boolean isCastling;
    private final boolean isEnPassant;
    private final PieceType promotionType; // null if no promotion
    private final boolean isFirstMove; // was movedPiece's first move? (for undo)

    private Move(Builder builder) {
        this.from = builder.from;
        this.to = builder.to;
        this.movedPiece = builder.movedPiece;
        this.capturedPiece = builder.capturedPiece;
        this.isCastling = builder.isCastling;
        this.isEnPassant = builder.isEnPassant;
        this.promotionType = builder.promotionType;
        this.isFirstMove = builder.isFirstMove;
    }

    // ─── Getters ──────────────────────────────────────────────────────

    public Position getFrom() {
        return from;
    }

    public Position getTo() {
        return to;
    }

    public Piece getMovedPiece() {
        return movedPiece;
    }

    public Piece getCapturedPiece() {
        return capturedPiece;
    }

    public boolean isCastling() {
        return isCastling;
    }

    public boolean isEnPassant() {
        return isEnPassant;
    }

    public PieceType getPromotionType() {
        return promotionType;
    }

    public boolean isPromotion() {
        return promotionType != null;
    }

    public boolean isCapture() {
        return capturedPiece != null;
    }

    public boolean wasFirstMove() {
        return isFirstMove;
    }

    @Override
    public String toString() {
        String base = from.toAlgebraic() + "→" + to.toAlgebraic();
        if (isCastling)
            return to.getCol() > from.getCol() ? "O-O" : "O-O-O";
        if (isPromotion())
            base += "=" + promotionType.getName().charAt(0);
        if (isCapture())
            base += " x" + capturedPiece.getType().getName();
        return base;
    }

    // ─── Builder Pattern ──────────────────────────────────────────────

    public static class Builder {
        private final Position from;
        private final Position to;
        private final Piece movedPiece;
        private Piece capturedPiece;
        private boolean isCastling;
        private boolean isEnPassant;
        private PieceType promotionType;
        private boolean isFirstMove;

        public Builder(Position from, Position to, Piece movedPiece) {
            this.from = from;
            this.to = to;
            this.movedPiece = movedPiece;
        }

        public Builder capturedPiece(Piece piece) {
            this.capturedPiece = piece;
            return this;
        }

        public Builder castling() {
            this.isCastling = true;
            return this;
        }

        public Builder enPassant() {
            this.isEnPassant = true;
            return this;
        }

        public Builder promotion(PieceType type) {
            this.promotionType = type;
            return this;
        }

        public Builder firstMove(boolean first) {
            this.isFirstMove = first;
            return this;
        }

        public Move build() {
            return new Move(this);
        }
    }
}
