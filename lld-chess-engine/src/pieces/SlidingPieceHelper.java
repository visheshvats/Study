package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;

import java.util.ArrayList;
import java.util.List;

/**
 * Helper for sliding pieces (Queen, Rook, Bishop).
 *
 * DRY Principle: All three sliding pieces share identical logic —
 * slide in a direction until hitting the edge or another piece.
 * Only the direction set differs (8 for Queen, 4 for Rook/Bishop).
 *
 * Extracting this prevents code duplication across three classes.
 */
public final class SlidingPieceHelper {

    private SlidingPieceHelper() {
    } // utility class

    /**
     * Generates all sliding moves in the given directions.
     * For each direction, slides until hitting:
     * - Board edge → stop
     * - Friendly piece → stop (don't include)
     * - Enemy piece → include (capture) then stop
     */
    public static List<Position> getSlidingMoves(
            Position position, Board board, int[][] directions, Color color) {

        List<Position> moves = new ArrayList<>();

        for (int[] dir : directions) {
            Position target = position.offset(dir[0], dir[1]);

            while (target.isValid()) {
                Piece occupant = board.getPieceAt(target);

                if (occupant == null) {
                    moves.add(target); // Empty square: keep sliding
                } else if (occupant.getColor() != color) {
                    moves.add(target); // Enemy: capture, then stop
                    break;
                } else {
                    break; // Friendly: blocked
                }

                target = target.offset(dir[0], dir[1]);
            }
        }

        return moves;
    }
}
