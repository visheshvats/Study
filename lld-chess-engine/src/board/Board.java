package src.board;

import src.core.Position;
import src.enums.Color;
import src.enums.PieceType;
import src.pieces.Piece;
import src.pieces.PieceFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents the 8×8 chess board.
 *
 * Design decisions:
 * - SINGLE RESPONSIBILITY: Board just manages piece placement and state
 * queries.
 * It does NOT handle game rules, turn management, or check detection.
 * - FEN SUPPORT: Can initialize from/serialize to FEN strings (Forsyth-Edwards
 * Notation), the standard for describing chess positions.
 * - NULL FOR EMPTY: A null cell means no piece. We considered a Cell wrapper
 * (like Tic Tac Toe), but for chess the direct Piece[][] is cleaner since
 * we frequently need the Piece reference itself for move generation.
 * - DEFENSIVE COPYING: Position-based API prevents external code from
 * directly mutating the grid array.
 */
public class Board {

    private static final int SIZE = 8;
    private final Piece[][] grid;

    public Board() {
        this.grid = new Piece[SIZE][SIZE];
    }

    // ─── Piece Access ─────────────────────────────────────────────────

    public Piece getPieceAt(Position pos) {
        if (!pos.isValid())
            return null;
        return grid[pos.getRow()][pos.getCol()];
    }

    public void setPieceAt(Position pos, Piece piece) {
        grid[pos.getRow()][pos.getCol()] = piece;
    }

    public void removePiece(Position pos) {
        grid[pos.getRow()][pos.getCol()] = null;
    }

    /**
     * Moves a piece from one position to another.
     * Returns the captured piece (or null).
     * Does NOT validate the move — that's the Game's job.
     */
    public Piece movePiece(Position from, Position to) {
        Piece piece = getPieceAt(from);
        Piece captured = getPieceAt(to);
        setPieceAt(to, piece);
        removePiece(from);
        return captured;
    }

    // ─── Board queries ────────────────────────────────────────────────

    /**
     * Finds the position of the King of the given color.
     * Returns null if not found (shouldn't happen in a valid game).
     */
    public Position findKing(Color color) {
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                Piece p = grid[r][c];
                if (p != null && p.getType() == PieceType.KING && p.getColor() == color) {
                    return new Position(r, c);
                }
            }
        }
        return null;
    }

    /**
     * Returns all positions containing pieces of the given color.
     */
    public List<Position> getPiecePositions(Color color) {
        List<Position> positions = new ArrayList<>();
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                Piece p = grid[r][c];
                if (p != null && p.getColor() == color) {
                    positions.add(new Position(r, c));
                }
            }
        }
        return positions;
    }

    /**
     * Returns all pieces of the given color.
     */
    public List<Piece> getPieces(Color color) {
        List<Piece> pieces = new ArrayList<>();
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                Piece p = grid[r][c];
                if (p != null && p.getColor() == color) {
                    pieces.add(p);
                }
            }
        }
        return pieces;
    }

    /**
     * Checks if the given square is attacked by any piece of the given color.
     * Used for check detection and castling validation.
     */
    public boolean isSquareAttacked(Position square, Color attackerColor) {
        List<Position> attackerPositions = getPiecePositions(attackerColor);
        for (Position pos : attackerPositions) {
            Piece attacker = getPieceAt(pos);
            List<Position> attacks = attacker.getPseudoLegalMoves(pos, this);
            if (attacks.contains(square)) {
                return true;
            }
        }
        return false;
    }

    // ─── FEN Support ──────────────────────────────────────────────────

    /**
     * Sets up the board from the piece-placement part of a FEN string.
     * Example: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
     * Ranks are listed from 8 (top/black side) to 1 (bottom/white side).
     */
    public void setupFromFen(String piecePlacement) {
        // Clear board
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                grid[r][c] = null;
            }
        }

        String[] ranks = piecePlacement.split("/");
        for (int i = 0; i < ranks.length; i++) {
            int row = 7 - i; // FEN starts from rank 8 (row 7)
            int col = 0;
            for (char ch : ranks[i].toCharArray()) {
                if (Character.isDigit(ch)) {
                    col += ch - '0'; // Skip empty squares
                } else {
                    grid[row][col] = PieceFactory.fromFenChar(ch);
                    col++;
                }
            }
        }
    }

    /**
     * Generates the piece-placement part of a FEN string from the current board.
     */
    public String toFen() {
        StringBuilder sb = new StringBuilder();
        for (int r = 7; r >= 0; r--) { // Start from rank 8
            int emptyCount = 0;
            for (int c = 0; c < SIZE; c++) {
                Piece p = grid[r][c];
                if (p == null) {
                    emptyCount++;
                } else {
                    if (emptyCount > 0) {
                        sb.append(emptyCount);
                        emptyCount = 0;
                    }
                    sb.append(PieceFactory.toFenChar(p));
                }
            }
            if (emptyCount > 0)
                sb.append(emptyCount);
            if (r > 0)
                sb.append('/');
        }
        return sb.toString();
    }

    /**
     * Sets up the standard starting position.
     */
    public void setupStartingPosition() {
        setupFromFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR");
    }

    // ─── Display ──────────────────────────────────────────────────────

    /**
     * Pretty-prints the board with Unicode pieces, coordinates, and borders.
     */
    public void printBoard() {
        System.out.println();
        System.out.println("  ┌───┬───┬───┬───┬───┬───┬───┬───┐");

        for (int r = 7; r >= 0; r--) { // Print from rank 8 down to rank 1
            System.out.print((r + 1) + " │");
            for (int c = 0; c < SIZE; c++) {
                Piece p = grid[r][c];
                String display = p != null ? p.getSymbol() : " ";
                System.out.print(" " + display + " │");
            }
            System.out.println();

            if (r > 0) {
                System.out.println("  ├───┼───┼───┼───┼───┼───┼───┼───┤");
            }
        }

        System.out.println("  └───┴───┴───┴───┴───┴───┴───┴───┘");
        System.out.println("    a   b   c   d   e   f   g   h");
        System.out.println();
    }

    public int getSize() {
        return SIZE;
    }
}
