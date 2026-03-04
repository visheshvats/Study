package src;

/**
 * Observer Pattern — Game End Notification Interface.
 *
 * Observers are notified when a game ends (win or draw).
 * The Scoreboard implements this to auto-update scores.
 *
 * Decoupling benefit: Game doesn't know what observers do.
 * You could add a Logger, a UI updater, or a stats tracker
 * without touching the Game class at all.
 */
public interface GameObserver {
    void onGameEnd(Game game);
}
