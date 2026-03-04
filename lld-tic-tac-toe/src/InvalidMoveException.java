package src;

/**
 * Custom exception for invalid game moves.
 *
 * Thrown when:
 * - A player tries to place on an already-occupied cell
 * - A move is made after the game has ended
 * - Row/column coordinates are out of bounds
 *
 * Using a custom exception is cleaner than catching generic RuntimeException.
 * It makes the API self-documenting: callers know exactly what can go wrong.
 */
public class InvalidMoveException extends RuntimeException {

    public InvalidMoveException(String message) {
        super(message);
    }
}
