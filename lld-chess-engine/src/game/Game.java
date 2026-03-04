package src.game;

import src.board.Board;
import src.core.Move;
import src.core.Position;
import src.enums.Color;
import src.enums.GameStatus;
import src.enums.PieceType;
import src.pieces.*;

import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * The central game orchestrator. Manages turns, validates moves,
 * handles special rules (castling, en passant, promotion),
 * detects check/checkmate/stalemate, and supports undo.
 *
 * Design patterns used:
 * 1. STRATEGY: Delegates move generation to each Piece subclass.
 * 2. OBSERVER: Notifies observers on move/undo/game-end events.
 * 3. COMMAND: Each Move is a command object stored in moveHistory
 * for full undo support.
 *
 * Thread safety: makeMove() and undoMove() are synchronized.
 */
public class Game {

    private final Board board;
    private Color currentTurn;
    private GameStatus status;
    private Position enPassantTarget; // square that can be captured via en passant
    private final Deque<Move> moveHistory;
    private final List<GameObserver> observers;

    public Game() {
        this.board = new Board();
        this.board.setupStartingPosition();
        this.currentTurn = Color.WHITE;
        this.status = GameStatus.ACTIVE;
        this.enPassantTarget = null;
        this.moveHistory = new LinkedList<>();
        this.observers = new CopyOnWriteArrayList<>();
    }

    public Game(String fen) {
        this.board = new Board();
        this.moveHistory = new LinkedList<>();
        this.observers = new CopyOnWriteArrayList<>();
        loadFen(fen);
    }

    // ─── Observer Management ────────────────────────────────────────

    public void addObserver(GameObserver observer) {
        observers.add(observer);
    }

    private void notifyMoveMade(Move move) {
        String fen = board.toFen();
        for (GameObserver obs : observers)
            obs.onMoveMade(move, fen);
    }

    private void notifyGameEnd(String result) {
        for (GameObserver obs : observers)
            obs.onGameEnd(result);
    }

    private void notifyMoveUndone(Move move) {
        String fen = board.toFen();
        for (GameObserver obs : observers)
            obs.onMoveUndone(move, fen);
    }

    // ─── Core Move Execution ────────────────────────────────────────

    /**
     * Attempts to make a move from algebraic notation (e.g., "e2", "e4").
     * Handles all validation, special rules, and game-state updates.
     *
     * @return The executed Move object (for undo), or null if invalid
     */
    public synchronized Move makeMove(String fromStr, String toStr) {
        return makeMove(fromStr, toStr, null);
    }

    /**
     * Makes a move with optional promotion type (for pawn promotion).
     */
    public synchronized Move makeMove(String fromStr, String toStr, PieceType promotionType) {
        if (status.isTerminal()) {
            System.out.println("  ❌ Game is already over: " + status);
            return null;
        }

        Position from = Position.fromAlgebraic(fromStr);
        Position to = Position.fromAlgebraic(toStr);

        Piece piece = board.getPieceAt(from);
        if (piece == null) {
            System.out.println("  ❌ No piece at " + fromStr);
            return null;
        }
        if (piece.getColor() != currentTurn) {
            System.out.println("  ❌ It's " + currentTurn + "'s turn, not " + piece.getColor() + "'s");
            return null;
        }

        // Generate legal moves for this piece
        List<Move> legalMoves = getLegalMovesForPiece(from);
        Move selectedMove = null;
        for (Move m : legalMoves) {
            if (m.getTo().equals(to)) {
                selectedMove = m;
                break;
            }
        }

        if (selectedMove == null) {
            System.out.println("  ❌ Illegal move: " + fromStr + " → " + toStr);
            return null;
        }

        // Handle promotion
        if (piece.getType() == PieceType.PAWN && (to.getRow() == 0 || to.getRow() == 7)) {
            if (promotionType == null)
                promotionType = PieceType.QUEEN; // default auto-queen
            selectedMove = new Move.Builder(from, to, piece)
                    .capturedPiece(board.getPieceAt(to))
                    .promotion(promotionType)
                    .firstMove(!piece.hasMoved())
                    .build();
        }

        // Execute the move
        executeMove(selectedMove);
        moveHistory.push(selectedMove);

        // Update en passant target
        updateEnPassantTarget(selectedMove);

        // Notify observers
        notifyMoveMade(selectedMove);

        // Switch turn and check game state
        currentTurn = currentTurn.opposite();
        updateGameStatus();

        return selectedMove;
    }

    /**
     * Applies a Move to the board. Handles castling, en passant, promotion.
     */
    private void executeMove(Move move) {
        Position from = move.getFrom();
        Position to = move.getTo();
        Piece piece = move.getMovedPiece();

        if (move.isCastling()) {
            // Move King
            board.movePiece(from, to);
            piece.setMoved(true);

            // Move Rook
            boolean kingside = to.getCol() > from.getCol();
            Position rookFrom = new Position(from.getRow(), kingside ? 7 : 0);
            Position rookTo = new Position(from.getRow(), kingside ? 5 : 3);
            Piece rook = board.getPieceAt(rookFrom);
            board.movePiece(rookFrom, rookTo);
            if (rook != null)
                rook.setMoved(true);

        } else if (move.isEnPassant()) {
            // Capture the pawn on the adjacent square (not the target square)
            board.movePiece(from, to);
            piece.setMoved(true);
            int capturedRow = from.getRow(); // en passant captured pawn is on same row
            board.removePiece(new Position(capturedRow, to.getCol()));

        } else if (move.isPromotion()) {
            board.removePiece(from);
            Piece promoted = PieceFactory.create(move.getPromotionType(), piece.getColor());
            promoted.setMoved(true);
            board.setPieceAt(to, promoted);

        } else {
            // Normal move
            board.movePiece(from, to);
            piece.setMoved(true);
        }
    }

    /**
     * Sets en passant target if a pawn just double-pushed.
     */
    private void updateEnPassantTarget(Move move) {
        Piece piece = move.getMovedPiece();
        if (piece.getType() == PieceType.PAWN) {
            int rowDiff = Math.abs(move.getTo().getRow() - move.getFrom().getRow());
            if (rowDiff == 2) {
                int epRow = (move.getFrom().getRow() + move.getTo().getRow()) / 2;
                enPassantTarget = new Position(epRow, move.getFrom().getCol());
                return;
            }
        }
        enPassantTarget = null;
    }

    // ─── Undo (Command Pattern) ─────────────────────────────────────

    /**
     * Undoes the last move. Command pattern in action — each Move stores
     * enough state to fully reverse the operation.
     */
    public synchronized boolean undoMove() {
        if (moveHistory.isEmpty()) {
            System.out.println("  ❌ No moves to undo.");
            return false;
        }

        Move move = moveHistory.pop();
        Position from = move.getFrom();
        Position to = move.getTo();
        Piece piece = move.getMovedPiece();

        if (move.isCastling()) {
            // Undo King
            board.movePiece(to, from);
            piece.setMoved(!move.wasFirstMove());

            // Undo Rook
            boolean kingside = to.getCol() > from.getCol();
            Position rookTo = new Position(from.getRow(), kingside ? 5 : 3);
            Position rookFrom = new Position(from.getRow(), kingside ? 7 : 0);
            Piece rook = board.getPieceAt(rookTo);
            board.movePiece(rookTo, rookFrom);
            if (rook != null)
                rook.setMoved(false);

        } else if (move.isEnPassant()) {
            board.movePiece(to, from);
            piece.setMoved(!move.wasFirstMove());
            // Restore the captured pawn
            int capturedRow = from.getRow();
            Position capturedPos = new Position(capturedRow, to.getCol());
            board.setPieceAt(capturedPos, move.getCapturedPiece());

        } else if (move.isPromotion()) {
            board.removePiece(to);
            board.setPieceAt(from, piece);
            piece.setMoved(!move.wasFirstMove());
            if (move.getCapturedPiece() != null) {
                board.setPieceAt(to, move.getCapturedPiece());
            }

        } else {
            board.movePiece(to, from);
            piece.setMoved(!move.wasFirstMove());
            if (move.getCapturedPiece() != null) {
                board.setPieceAt(to, move.getCapturedPiece());
            }
        }

        // Restore en passant target from the move before this one
        enPassantTarget = null;
        if (!moveHistory.isEmpty()) {
            Move prev = moveHistory.peek();
            if (prev.getMovedPiece().getType() == PieceType.PAWN) {
                int diff = Math.abs(prev.getTo().getRow() - prev.getFrom().getRow());
                if (diff == 2) {
                    int epRow = (prev.getFrom().getRow() + prev.getTo().getRow()) / 2;
                    enPassantTarget = new Position(epRow, prev.getFrom().getCol());
                }
            }
        }

        currentTurn = currentTurn.opposite();
        status = GameStatus.ACTIVE;

        notifyMoveUndone(move);
        return true;
    }

    // ─── Legal Move Generation ──────────────────────────────────────

    /**
     * Returns all legal moves for a piece at the given position.
     * Filters pseudo-legal moves by removing those that leave own King in check.
     */
    public List<Move> getLegalMovesForPiece(Position pos) {
        Piece piece = board.getPieceAt(pos);
        if (piece == null || piece.getColor() != currentTurn) {
            return new ArrayList<>();
        }

        List<Move> legalMoves = new ArrayList<>();
        List<Position> pseudoTargets = piece.getPseudoLegalMoves(pos, board);

        for (Position target : pseudoTargets) {
            Move.Builder builder = new Move.Builder(pos, target, piece)
                    .firstMove(!piece.hasMoved());

            Piece captured = board.getPieceAt(target);
            if (captured != null)
                builder.capturedPiece(captured);

            Move move = builder.build();

            // Test if this move leaves own King in check
            if (!leavesKingInCheck(move)) {
                legalMoves.add(move);
            }
        }

        // Add en passant moves
        if (piece.getType() == PieceType.PAWN && enPassantTarget != null) {
            int direction = piece.getColor() == Color.WHITE ? 1 : -1;
            if (pos.getRow() + direction == enPassantTarget.getRow()
                    && Math.abs(pos.getCol() - enPassantTarget.getCol()) == 1) {

                // The captured pawn is on the same row as the moving pawn
                Position capturedPawnPos = new Position(pos.getRow(), enPassantTarget.getCol());
                Piece capturedPawn = board.getPieceAt(capturedPawnPos);

                if (capturedPawn != null && capturedPawn.getType() == PieceType.PAWN
                        && capturedPawn.getColor() != piece.getColor()) {

                    Move epMove = new Move.Builder(pos, enPassantTarget, piece)
                            .enPassant()
                            .capturedPiece(capturedPawn)
                            .firstMove(!piece.hasMoved())
                            .build();

                    if (!leavesKingInCheck(epMove)) {
                        legalMoves.add(epMove);
                    }
                }
            }
        }

        // Add castling moves (only for King)
        if (piece.getType() == PieceType.KING && !piece.hasMoved()) {
            addCastlingMoves(pos, piece, legalMoves);
        }

        return legalMoves;
    }

    /**
     * Checks if executing a move would leave the moving side's King in check.
     * Temporarily makes the move, checks, then undoes it.
     */
    private boolean leavesKingInCheck(Move move) {
        // Simulate move
        Position from = move.getFrom();
        Position to = move.getTo();
        Piece piece = move.getMovedPiece();
        Piece captured = board.getPieceAt(to);

        // Special handling for en passant capture
        Position enPassantCapturePos = null;
        Piece enPassantCaptured = null;
        if (move.isEnPassant()) {
            enPassantCapturePos = new Position(from.getRow(), to.getCol());
            enPassantCaptured = board.getPieceAt(enPassantCapturePos);
            board.removePiece(enPassantCapturePos);
        }

        board.setPieceAt(to, piece);
        board.removePiece(from);

        // Find our King's position
        Position kingPos = piece.getType() == PieceType.KING
                ? to
                : board.findKing(piece.getColor());

        boolean inCheck = board.isSquareAttacked(kingPos, piece.getColor().opposite());

        // Undo simulation
        board.setPieceAt(from, piece);
        board.setPieceAt(to, captured);

        if (enPassantCapturePos != null) {
            board.setPieceAt(enPassantCapturePos, enPassantCaptured);
        }

        return inCheck;
    }

    /**
     * Adds legal castling moves for the King.
     * Conditions: King hasn't moved, Rook hasn't moved, no pieces between,
     * King doesn't pass through or land on attacked squares, King not in check.
     */
    private void addCastlingMoves(Position kingPos, Piece king, List<Move> moves) {
        Color color = king.getColor();
        int row = kingPos.getRow();

        // Can't castle out of check
        if (board.isSquareAttacked(kingPos, color.opposite()))
            return;

        // Kingside (O-O)
        Piece kRook = board.getPieceAt(new Position(row, 7));
        if (kRook != null && kRook.getType() == PieceType.ROOK
                && kRook.getColor() == color && !kRook.hasMoved()) {
            // Squares between must be empty
            if (board.getPieceAt(new Position(row, 5)) == null
                    && board.getPieceAt(new Position(row, 6)) == null) {
                // Squares King passes through must not be attacked
                if (!board.isSquareAttacked(new Position(row, 5), color.opposite())
                        && !board.isSquareAttacked(new Position(row, 6), color.opposite())) {
                    moves.add(new Move.Builder(kingPos, new Position(row, 6), king)
                            .castling().firstMove(true).build());
                }
            }
        }

        // Queenside (O-O-O)
        Piece qRook = board.getPieceAt(new Position(row, 0));
        if (qRook != null && qRook.getType() == PieceType.ROOK
                && qRook.getColor() == color && !qRook.hasMoved()) {
            // Squares between must be empty
            if (board.getPieceAt(new Position(row, 1)) == null
                    && board.getPieceAt(new Position(row, 2)) == null
                    && board.getPieceAt(new Position(row, 3)) == null) {
                // King passes through d-file and c-file
                if (!board.isSquareAttacked(new Position(row, 3), color.opposite())
                        && !board.isSquareAttacked(new Position(row, 2), color.opposite())) {
                    moves.add(new Move.Builder(kingPos, new Position(row, 2), king)
                            .castling().firstMove(true).build());
                }
            }
        }
    }

    /**
     * Returns ALL legal moves for the current player.
     */
    public List<Move> getAllLegalMoves() {
        List<Move> allMoves = new ArrayList<>();
        for (Position pos : board.getPiecePositions(currentTurn)) {
            allMoves.addAll(getLegalMovesForPiece(pos));
        }
        return allMoves;
    }

    // ─── Game State Detection ───────────────────────────────────────

    /**
     * Updates game status after a move: check, checkmate, stalemate, draw.
     */
    private void updateGameStatus() {
        List<Move> legalMoves = getAllLegalMoves();
        boolean inCheck = isInCheck(currentTurn);

        if (legalMoves.isEmpty()) {
            if (inCheck) {
                // Checkmate! The OTHER player wins
                status = currentTurn == Color.WHITE ? GameStatus.BLACK_WINS : GameStatus.WHITE_WINS;
                String winner = currentTurn.opposite().toString();
                System.out.println("  ♚ CHECKMATE! " + winner + " wins!");
                notifyGameEnd(winner + " wins by checkmate");
            } else {
                // Stalemate
                status = GameStatus.STALEMATE;
                System.out.println("  🤝 STALEMATE! It's a draw.");
                notifyGameEnd("Draw by stalemate");
            }
        } else if (inCheck) {
            System.out.println("  ⚠️  " + currentTurn + " is in CHECK!");
        }

        // Check for insufficient material
        if (isInsufficientMaterial()) {
            status = GameStatus.DRAW;
            System.out.println("  🤝 DRAW — insufficient material!");
            notifyGameEnd("Draw by insufficient material");
        }
    }

    /**
     * Returns true if the given side's King is currently in check.
     */
    public boolean isInCheck(Color color) {
        Position kingPos = board.findKing(color);
        if (kingPos == null)
            return false;
        return board.isSquareAttacked(kingPos, color.opposite());
    }

    /**
     * Detects insufficient material draws:
     * - King vs King
     * - King + Bishop vs King
     * - King + Knight vs King
     */
    private boolean isInsufficientMaterial() {
        List<Piece> whitePieces = board.getPieces(Color.WHITE);
        List<Piece> blackPieces = board.getPieces(Color.BLACK);

        // King vs King
        if (whitePieces.size() == 1 && blackPieces.size() == 1)
            return true;

        // King + minor piece vs King
        if (whitePieces.size() == 1 && blackPieces.size() == 2) {
            return blackPieces.stream()
                    .anyMatch(p -> p.getType() == PieceType.BISHOP || p.getType() == PieceType.KNIGHT);
        }
        if (blackPieces.size() == 1 && whitePieces.size() == 2) {
            return whitePieces.stream()
                    .anyMatch(p -> p.getType() == PieceType.BISHOP || p.getType() == PieceType.KNIGHT);
        }

        return false;
    }

    // ─── FEN ────────────────────────────────────────────────────────

    /**
     * Loads a full FEN string. Example:
     * "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
     */
    private void loadFen(String fen) {
        String[] parts = fen.split(" ");
        board.setupFromFen(parts[0]);
        currentTurn = parts.length > 1 && parts[1].equals("b") ? Color.BLACK : Color.WHITE;
        status = GameStatus.ACTIVE;
        enPassantTarget = null;

        // Parse en passant target
        if (parts.length > 3 && !parts[3].equals("-")) {
            enPassantTarget = Position.fromAlgebraic(parts[3]);
        }

        // Parse castling rights (mark rooks/kings as moved if they can't castle)
        if (parts.length > 2) {
            String castling = parts[2];
            // If a castling right is missing, mark the corresponding piece as moved
            Piece whiteKing = board.getPieceAt(new Position(0, 4));
            Piece blackKing = board.getPieceAt(new Position(7, 4));

            if (!castling.contains("K") && !castling.contains("Q")) {
                if (whiteKing != null)
                    whiteKing.setMoved(true);
            }
            if (!castling.contains("k") && !castling.contains("q")) {
                if (blackKing != null)
                    blackKing.setMoved(true);
            }
            if (!castling.contains("K")) {
                Piece rook = board.getPieceAt(new Position(0, 7));
                if (rook != null)
                    rook.setMoved(true);
            }
            if (!castling.contains("Q")) {
                Piece rook = board.getPieceAt(new Position(0, 0));
                if (rook != null)
                    rook.setMoved(true);
            }
            if (!castling.contains("k")) {
                Piece rook = board.getPieceAt(new Position(7, 7));
                if (rook != null)
                    rook.setMoved(true);
            }
            if (!castling.contains("q")) {
                Piece rook = board.getPieceAt(new Position(7, 0));
                if (rook != null)
                    rook.setMoved(true);
            }
        }
    }

    // ─── Getters ────────────────────────────────────────────────────

    public Board getBoard() {
        return board;
    }

    public Color getCurrentTurn() {
        return currentTurn;
    }

    public GameStatus getStatus() {
        return status;
    }

    public Deque<Move> getMoveHistory() {
        return moveHistory;
    }

    public Position getEnPassantTarget() {
        return enPassantTarget;
    }
}
