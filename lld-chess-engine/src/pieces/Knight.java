package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * Knight — moves in an L-shape: 2 squares in one direction + 1 perpendicular.
 *
 * Key property: Knights JUMP over pieces — they are the only piece
 * that can do this. No sliding logic needed, just check 8 target squares.
 */
public class Knight extends Piece {

    private static final int[][] OFFSETS = {
            { -2, -1 }, { -2, 1 }, { -1, -2 }, { -1, 2 },
            { 1, -2 }, { 1, 2 }, { 2, -1 }, { 2, 1 }
    };

    public Knight(Color color) {
        super(color, PieceType.KNIGHT);
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
