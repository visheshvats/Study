package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * Rook — slides horizontally or vertically any number of squares.
 */
public class Rook extends Piece {

    private static final int[][] DIRECTIONS = {
            { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 }
    };

    public Rook(Color color) {
        super(color, PieceType.ROOK);
    }

    @Override
    public List<Position> getPseudoLegalMoves(Position position, Board board) {
        return SlidingPieceHelper.getSlidingMoves(position, board, DIRECTIONS, getColor());
    }
}
