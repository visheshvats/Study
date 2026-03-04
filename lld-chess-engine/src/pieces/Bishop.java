package src.pieces;

import src.board.Board;
import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * Bishop — slides diagonally any number of squares.
 */
public class Bishop extends Piece {

    private static final int[][] DIRECTIONS = {
            { -1, -1 }, { -1, 1 }, { 1, -1 }, { 1, 1 }
    };

    public Bishop(Color color) {
        super(color, PieceType.BISHOP);
    }

    @Override
    public List<Position> getPseudoLegalMoves(Position position, Board board) {
        return SlidingPieceHelper.getSlidingMoves(position, board, DIRECTIONS, getColor());
    }
}
