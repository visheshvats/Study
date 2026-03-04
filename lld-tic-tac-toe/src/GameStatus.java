package src;

/**
 * Defines all possible states of a game.
 *
 * Design note: We use WINNER_X and WINNER_O instead of a generic WINNER
 * with a separate winner field. This makes status checks simpler:
 * if (status == GameStatus.WINNER_X)
 * vs.
 * if (status == GameStatus.WINNER && winner.getSymbol() == Symbol.X)
 *
 * The enum is self-contained — you can determine the winner from status alone.
 */
public enum GameStatus {
    IN_PROGRESS,
    WINNER_X,
    WINNER_O,
    DRAW
}
