package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * Queen — combines Rook (straight lines) and Bishop (diagonals).
 * Slides any number of squares in 8 directions until blocked.
 */
public class Queen extends Piece {

    private static final int[][] DIRECTIONS = {
            { -1, -1 }, { -1, 0 }, { -1, 1 },
            { 0, -1 }, { 0, 1 },
            { 1, -1 }, { 1, 0 }, { 1, 1 }
    };

    public Queen(Color color) {
        super(color, PieceType.QUEEN);
    }

    @Override
    public List<Position> getPseudoLegalMoves(Position position, Board board) {
        return SlidingPieceHelper.getSlidingMoves(position, board, DIRECTIONS, getColor());
    }
}
