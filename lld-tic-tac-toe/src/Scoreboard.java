package src;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Tracks wins across multiple games.
 *
 * Implements GameObserver (Observer Pattern) — automatically updates
 * when a game ends. The Scoreboard is decoupled from Game: it doesn't
 * know when games start or how moves work. It just receives onGameEnd().
 *
 * Thread Safety:
 * - ConcurrentHashMap for the scores map
 * - merge() atomically gets the current value (or 0 if absent), adds 1,
 * and stores the result — no explicit synchronization needed.
 */
public class Scoreboard implements GameObserver {

    private final Map<String, Integer> scores;

    public Scoreboard() {
        this.scores = new ConcurrentHashMap<>();
    }

    /**
     * Called automatically when any observed game ends.
     * Only records a win — draws don't update the scoreboard.
     */
    @Override
    public void onGameEnd(Game game) {
        Player winner = game.getWinner();
        if (winner != null) {
            // merge(): atomically increments the score (or sets to 1 if first win)
            scores.merge(winner.getName(), 1, Integer::sum);
        }
    }

    public int getScore(String playerName) {
        return scores.getOrDefault(playerName, 0);
    }

    public void printScoreboard() {
        System.out.println("═══════════════════════════");
        System.out.println("         SCOREBOARD        ");
        System.out.println("═══════════════════════════");
        if (scores.isEmpty()) {
            System.out.println("  No wins recorded yet.");
        } else {
            scores.forEach((name, score) -> System.out.printf("  %-15s : %d%n", name, score));
        }
        System.out.println("═══════════════════════════\n");
    }
}
