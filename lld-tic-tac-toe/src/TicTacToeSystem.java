package src;

/**
 * Singleton Facade — the public entry point for the entire system.
 *
 * External code only interacts with TicTacToeSystem. It doesn't need to
 * know about Board, Cell, WinningStrategy, or GameObserver.
 *
 * Design Patterns used:
 * 1. SINGLETON: Only one TicTacToeSystem exists. The shared Scoreboard
 * persists across all games.
 * 2. FACADE: Hides the complexity of Game, Board, Scoreboard, and
 * observer wiring behind a simple 3-method API.
 *
 * Singleton Implementation Details:
 * - Double-checked locking: First check avoids synchronization cost when
 * instance already exists. Second check (inside synchronized) handles
 * the race condition where two threads both pass the first check.
 * - volatile: Ensures that when one thread creates the instance, other
 * threads immediately see the FULLY constructed object. Without volatile,
 * instruction reordering could cause another thread to see a partially
 * constructed instance.
 * - resetInstance(): Allows resetting the singleton between unit tests.
 * In production, remove this or make it package-private.
 */
public class TicTacToeSystem {

    private static volatile TicTacToeSystem instance; // volatile is critical!

    private final Scoreboard scoreboard;
    private Game currentGame;

    // Private constructor — prevents direct instantiation
    private TicTacToeSystem() {
        this.scoreboard = new Scoreboard();
        this.currentGame = null;
    }

    /**
     * Double-checked locking singleton accessor.
     */
    public static TicTacToeSystem getInstance() {
        if (instance == null) { // First check (no lock)
            synchronized (TicTacToeSystem.class) {
                if (instance == null) { // Second check (with lock)
                    instance = new TicTacToeSystem();
                }
            }
        }
        return instance;
    }

    /**
     * For testing only — resets the singleton so tests are independent.
     */
    public static synchronized void resetInstance() {
        instance = null;
    }

    // ─── Facade API ──────────────────────────────────────────────────────────

    /**
     * Creates a new game and wires the scoreboard as an observer.
     * The Scoreboard will automatically update when this game ends.
     */
    public void createGame(Player player1, Player player2) {
        currentGame = new Game(player1, player2, 3);
        currentGame.addObserver(scoreboard); // Wire observer
        System.out.println("New game started: " + player1 + " vs " + player2);
        currentGame.getBoard().printBoard();
    }

    /**
     * Delegates the move to the current game.
     */
    public void makeMove(int row, int col) {
        if (currentGame == null) {
            throw new IllegalStateException("No game in progress. Call createGame() first.");
        }
        currentGame.makeMove(row, col);
    }

    /**
     * Prints the persistent scoreboard.
     */
    public void printScoreboard() {
        scoreboard.printScoreboard();
    }

    public Game getCurrentGame() {
        return currentGame;
    }

    public Scoreboard getScoreboard() {
        return scoreboard;
    }
}
