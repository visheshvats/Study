package src.game;

import src.core.Move;

/**
 * Observer implementation — logs all moves and game events to console.
 *
 * Demonstrates the Observer pattern: MoveLogger receives notifications
 * without the Game knowing it exists. You could add PgnRecorder,
 * StatsTracker, etc. without touching Game.
 */
public class MoveLogger implements GameObserver {

    private int moveNumber = 0;

    @Override
    public void onMoveMade(Move move, String fen) {
        moveNumber++;
        System.out.println("  📝 Move #" + moveNumber + ": " + move);
    }

    @Override
    public void onGameEnd(String result) {
        System.out.println("  🏁 Game Over: " + result + " (Total moves: " + moveNumber + ")");
    }

    @Override
    public void onMoveUndone(Move move, String fen) {
        moveNumber--;
        System.out.println("  ↩️  Undid move: " + move);
    }
}
