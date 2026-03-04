package src;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Orchestrates gameplay: accepts moves, validates them, checks win/draw,
 * switches turns, and notifies observers when the game ends.
 *
 * Design decisions:
 *
 * 1. THREAD SAFETY: makeMove() is synchronized to prevent two threads from
 * making moves simultaneously (which would corrupt game state).
 * CopyOnWriteArrayList for observers allows safe iteration even if
 * observers are added during notification.
 *
 * 2. STRATEGY PATTERN: winningStrategies is a list of WinningStrategy objects.
 * Adding a new win condition = adding a new strategy. No changes to Game.
 *
 * 3. OBSERVER PATTERN: Observers are notified only when the game ends.
 * The Game doesn't know what observers do — it just calls onGameEnd().
 *
 * 4. SINGLE RESPONSIBILITY: Game coordinates; Board manages the grid;
 * Strategies detect wins; Scoreboard tracks scores.
 */
public class Game {

    private final Board board;
    private final List<Player> players;
    private int currentPlayerIndex;
    private GameStatus status;
    private final List<WinningStrategy> winningStrategies;
    private final List<GameObserver> observers;
    private Player winner; // null if draw or in progress

    public Game(Player player1, Player player2, int boardSize) {
        this.board = new Board(boardSize);
        this.players = new ArrayList<>();
        this.players.add(player1);
        this.players.add(player2);
        this.currentPlayerIndex = 0;
        this.status = GameStatus.IN_PROGRESS;
        this.winner = null;

        // Register all three winning strategies
        this.winningStrategies = new ArrayList<>();
        this.winningStrategies.add(new RowWinningStrategy());
        this.winningStrategies.add(new ColumnWinningStrategy());
        this.winningStrategies.add(new DiagonalWinningStrategy());

        // Thread-safe list for observers
        this.observers = new CopyOnWriteArrayList<>();
    }

    // ─── Observer Management ────────────────────────────────────────────────

    public void addObserver(GameObserver observer) {
        observers.add(observer);
    }

    private void notifyObservers() {
        for (GameObserver observer : observers) {
            observer.onGameEnd(this);
        }
    }

    // ─── Core Gameplay ───────────────────────────────────────────────────────

    /**
     * Makes a move for the current player at (row, col).
     *
     * Flow:
     * 1. Fail fast if game is already over
     * 2. Validate cell is empty
     * 3. Place the symbol
     * 4. Check for win using all strategies
     * 5. Check for draw if no winner
     * 6. Switch to next player if game continues
     * 7. Notify observers if game ended
     */
    public synchronized void makeMove(int row, int col) {
        // Step 1: Fail fast
        if (status != GameStatus.IN_PROGRESS) {
            throw new InvalidMoveException("Game is already over. Status: " + status);
        }

        // Step 2: Validate cell
        if (!board.isCellEmpty(row, col)) {
            throw new InvalidMoveException(
                    "Cell (" + row + ", " + col + ") is already occupied.");
        }

        Player currentPlayer = players.get(currentPlayerIndex);
        Symbol symbol = currentPlayer.getSymbol();

        // Step 3: Place symbol
        board.placeSymbol(row, col, symbol);

        System.out.println(currentPlayer.getName() + " plays at (" + row + ", " + col + ")");
        board.printBoard();

        // Step 4: Check for win
        if (checkWin(row, col, symbol)) {
            status = (symbol == Symbol.X) ? GameStatus.WINNER_X : GameStatus.WINNER_O;
            winner = currentPlayer;
            System.out.println("🏆 " + currentPlayer.getName() + " wins!");
            notifyObservers();
            return;
        }

        // Step 5: Check for draw
        if (board.isFull()) {
            status = GameStatus.DRAW;
            System.out.println("🤝 It's a draw!");
            notifyObservers();
            return;
        }

        // Step 6: Switch player
        currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
    }

    /**
     * Iterates through all strategies. Returns true as soon as one matches.
     * Strategy pattern pays off here: adding a new win condition = new class.
     */
    private boolean checkWin(int row, int col, Symbol symbol) {
        for (WinningStrategy strategy : winningStrategies) {
            if (strategy.checkWin(board, row, col, symbol)) {
                return true;
            }
        }
        return false;
    }

    // ─── Getters ─────────────────────────────────────────────────────────────

    public GameStatus getStatus() {
        return status;
    }

    public Player getWinner() {
        return winner;
    }

    public Board getBoard() {
        return board;
    }

    public Player getCurrentPlayer() {
        return players.get(currentPlayerIndex);
    }
}
