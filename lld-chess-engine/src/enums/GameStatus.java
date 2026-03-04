package src.enums;

/**
 * All possible game states.
 *
 * Design: Mirrors the approach from the Tic Tac Toe LLD.
 * ACTIVE = game in progress.
 * Terminal states: WHITE_WINS, BLACK_WINS, STALEMATE, DRAW.
 * DRAW covers insufficient material, fifty-move rule, threefold repetition.
 */
public enum GameStatus {
    ACTIVE,
    WHITE_WINS,
    BLACK_WINS,
    STALEMATE,
    DRAW;

    public boolean isTerminal() {
        return this != ACTIVE;
    }
}
