package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * King — moves one square in any direction.
 *
 * NOTE: Castling is NOT generated here. It's handled by the Game class
 * because it requires knowledge of:
 * 1. Whether the King has moved
 * 2. Whether the Rook has moved
 * 3. Whether squares between them are attacked
 * This breaks single-responsibility if handled here.
 */
public class King extends Piece {

    private static final int[][] OFFSETS = {
            { -1, -1 }, { -1, 0 }, { -1, 1 },
            { 0, -1 }, { 0, 1 },
            { 1, -1 }, { 1, 0 }, { 1, 1 }
    };

    public King(Color color) {
        super(color, PieceType.KING);
    }

    @Override
    public List<Position> getPseudoLegalMoves(Position position, Board board) {
        List<Position> moves = new ArrayList<>();

        for (int[] offset : OFFSETS) {
            Position target = position.offset(offset[0], offset[1]);
            if (target.isValid()) {
                Piece occupant = board.getPieceAt(target);
                if (occupant == null || occupant.getColor() != getColor()) {
                    moves.add(target);
                }
            }
        }

        return moves;
    }
}
