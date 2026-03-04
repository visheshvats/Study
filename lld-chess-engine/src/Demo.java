package src;

import src.game.Game;
import src.game.MoveLogger;
import src.enums.GameStatus;

/**
 * Demo class — showcases the chess engine with three scenarios:
 *
 * 1. Scholar's Mate (4-move checkmate)
 * 2. Castling demonstration (kingside + queenside)
 * 3. Undo demonstration (Command pattern)
 *
 * All interaction goes through the Game class (Facade).
 */
public class Demo {

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════╗");
        System.out.println("║    ♔  LLD Chess Engine Demo  ♚         ║");
        System.out.println("╚══════════════════════════════════════════╝\n");

        scholarsMate();
        castlingDemo();
        undoDemo();
        enPassantDemo();
    }

    // ── Scenario 1: Scholar's Mate ─────────────────────────────────
    private static void scholarsMate() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  SCENARIO 1: Scholar's Mate (4 moves)");
        System.out.println("═══════════════════════════════════════");

        Game game = new Game();
        game.addObserver(new MoveLogger());
        game.getBoard().printBoard();

        game.makeMove("e2", "e4"); // 1. e4
        game.makeMove("e7", "e5"); // 1... e5
        game.makeMove("f1", "c4"); // 2. Bc4
        game.makeMove("b8", "c6"); // 2... Nc6
        game.makeMove("d1", "h5"); // 3. Qh5
        game.makeMove("g8", "f6"); // 3... Nf6??
        game.makeMove("h5", "f7"); // 4. Qxf7# — Checkmate!

        game.getBoard().printBoard();
        System.out.println("  Final Status: " + game.getStatus());
        System.out.println();
    }

    // ── Scenario 2: Castling ───────────────────────────────────────
    private static void castlingDemo() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  SCENARIO 2: Castling Demo");
        System.out.println("═══════════════════════════════════════");

        // Load a position where castling is possible
        String fen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1";
        Game game = new Game(fen);
        game.addObserver(new MoveLogger());

        System.out.println("  Position with castling available:");
        game.getBoard().printBoard();

        // White castles kingside (O-O)
        System.out.println("  White castles kingside (O-O):");
        game.makeMove("e1", "g1");
        game.getBoard().printBoard();

        // Black castles queenside (O-O-O)
        System.out.println("  Black castles queenside (O-O-O):");
        game.makeMove("e8", "c8");
        game.getBoard().printBoard();
    }

    // ── Scenario 3: Undo (Command Pattern) ─────────────────────────
    private static void undoDemo() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  SCENARIO 3: Undo Demo (Command Pattern)");
        System.out.println("═══════════════════════════════════════");

        Game game = new Game();
        game.addObserver(new MoveLogger());

        game.makeMove("e2", "e4");
        game.makeMove("e7", "e5");
        game.makeMove("g1", "f3");

        System.out.println("  Board after 3 moves:");
        game.getBoard().printBoard();

        System.out.println("  Undoing last move (Nf3)...");
        game.undoMove();
        game.getBoard().printBoard();

        System.out.println("  Undoing another move (e5)...");
        game.undoMove();
        game.getBoard().printBoard();

        System.out.println("  Move history size: " + game.getMoveHistory().size());
        System.out.println();
    }

    // ── Scenario 4: En Passant ──────────────────────────────────────
    private static void enPassantDemo() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  SCENARIO 4: En Passant Demo");
        System.out.println("═══════════════════════════════════════");

        // Set up a position where en passant is available
        // White pawn on e5, Black pawn about to double-push d7-d5
        String fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3";
        Game game = new Game(fen);
        game.addObserver(new MoveLogger());

        System.out.println("  En passant available: White pawn e5 can capture on d6");
        game.getBoard().printBoard();

        game.makeMove("e5", "d6"); // En passant capture!
        System.out.println("  After en passant capture:");
        game.getBoard().printBoard();
    }
}
