package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * Pawn — the most complex piece due to special rules:
 *
 * 1. FORWARD ONLY: Moves toward the opponent's side (up for White, down for
 * Black).
 * 2. DOUBLE PUSH: Can move 2 squares from starting position (row 1 for White,
 * row 6 for Black).
 * 3. CAPTURES DIAGONALLY: Unlike all other pieces, pawns capture differently
 * than they move.
 * 4. EN PASSANT: Handled by Game class (requires knowledge of opponent's last
 * move).
 * 5. PROMOTION: Handled by Game class (requires user choice of piece type).
 *
 * Direction is determined by color: White moves +1 row, Black moves -1 row.
 * Starting row: White = row 1 (rank 2), Black = row 6 (rank 7).
 */
public class Pawn extends Piece {

    public Pawn(Color color) {
        super(color, PieceType.PAWN);
    }

    @Override
    public List<Position> getPseudoLegalMoves(Position position, Board board) {
        List<Position> moves = new ArrayList<>();
        int direction = getColor() == Color.WHITE ? 1 : -1;
        int startRow = getColor() == Color.WHITE ? 1 : 6;

        // ── Single push forward ─────────────────────────────────
        Position oneForward = position.offset(direction, 0);
        if (oneForward.isValid() && board.getPieceAt(oneForward) == null) {
            moves.add(oneForward);

            // ── Double push from starting position ──────────────
            if (position.getRow() == startRow) {
                Position twoForward = position.offset(2 * direction, 0);
                if (twoForward.isValid() && board.getPieceAt(twoForward) == null) {
                    moves.add(twoForward);
                }
            }
        }

        // ── Diagonal captures ───────────────────────────────────
        for (int dc : new int[] { -1, 1 }) {
            Position capture = position.offset(direction, dc);
            if (capture.isValid()) {
                Piece occupant = board.getPieceAt(capture);
                if (occupant != null && occupant.getColor() != getColor()) {
                    moves.add(capture);
                }
            }
        }

        // En passant targets added by Game class (requires last-move context)
        return moves;
    }
}
