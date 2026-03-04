package src.game;

import src.core.Move;

/**
 * Observer Pattern — Game Event Notifications.
 *
 * Implementations can react to game events without the Game
 * knowing what they do. Supports:
 * - Move logging
 * - Score tracking
 * - UI updates
 * - PGN recording
 */
public interface GameObserver {

    /** Called after every move is executed. */
    void onMoveMade(Move move, String fen);

    /** Called when the game ends. */
    void onGameEnd(String result);

    /** Called when a move is undone. */
    void onMoveUndone(Move move, String fen);
}
