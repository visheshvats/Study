package src;

/**
 * Demo class — simulates three complete games to demonstrate the system.
 *
 * Game 1: Alice (X) wins via top row
 * Game 2: Bob (O) wins via main diagonal
 * Game 3: Draw — all cells filled, no winner
 *
 * Notice: The caller only interacts with TicTacToeSystem (the Facade).
 * It never touches Board, Cell, WinningStrategy, or Scoreboard directly.
 */
public class Demo {

    public static void main(String[] args) {
        TicTacToeSystem system = TicTacToeSystem.getInstance();

        Player alice = new Player("Alice", Symbol.X);
        Player bob = new Player("Bob", Symbol.O);

        // ── Game 1: Alice wins via top row ───────────────────────────────────
        System.out.println("╔══════════════════════════════╗");
        System.out.println("║         GAME 1               ║");
        System.out.println("╚══════════════════════════════╝");
        system.createGame(alice, bob);

        system.makeMove(0, 0); // Alice: X at (0,0)
        system.makeMove(1, 0); // Bob: O at (1,0)
        system.makeMove(0, 1); // Alice: X at (0,1)
        system.makeMove(1, 1); // Bob: O at (1,1)
        system.makeMove(0, 2); // Alice: X at (0,2) → Alice wins top row!

        system.printScoreboard();

        // ── Game 2: Bob wins via main diagonal ──────────────────────────────
        System.out.println("╔══════════════════════════════╗");
        System.out.println("║         GAME 2               ║");
        System.out.println("╚══════════════════════════════╝");
        system.createGame(alice, bob);

        system.makeMove(0, 1); // Alice: X at (0,1)
        system.makeMove(0, 0); // Bob: O at (0,0)
        system.makeMove(1, 2); // Alice: X at (1,2)
        system.makeMove(1, 1); // Bob: O at (1,1)
        system.makeMove(0, 2); // Alice: X at (0,2)
        system.makeMove(2, 2); // Bob: O at (2,2) → Bob wins main diagonal!

        system.printScoreboard();

        // ── Game 3: Draw ─────────────────────────────────────────────────────
        System.out.println("╔══════════════════════════════╗");
        System.out.println("║         GAME 3 (DRAW)        ║");
        System.out.println("╚══════════════════════════════╝");
        system.createGame(alice, bob);

        // Board fills up with no winner:
        // X O X
        // X X O
        // O X O
        system.makeMove(0, 0); // Alice: X
        system.makeMove(0, 1); // Bob: O
        system.makeMove(0, 2); // Alice: X
        system.makeMove(1, 2); // Bob: O
        system.makeMove(1, 0); // Alice: X
        system.makeMove(2, 0); // Bob: O
        system.makeMove(1, 1); // Alice: X
        system.makeMove(2, 2); // Bob: O
        system.makeMove(2, 1); // Alice: X → Draw!

        system.printScoreboard();

        // ── Invalid Move Demo ─────────────────────────────────────────────────
        System.out.println("╔══════════════════════════════╗");
        System.out.println("║     INVALID MOVE DEMO        ║");
        System.out.println("╚══════════════════════════════╝");
        system.createGame(alice, bob);
        system.makeMove(0, 0); // Alice plays (0,0)
        try {
            system.makeMove(0, 0); // Bob tries the same cell!
        } catch (InvalidMoveException e) {
            System.out.println("✅ Caught expected error: " + e.getMessage());
        }
    }
}
