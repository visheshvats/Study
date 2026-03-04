package src;

/**
 * Represents a player in the game.
 *
 * Design decisions:
 * - IMMUTABLE: Both fields are final. Once created, a player's name and
 * symbol never change. This prevents bugs where someone accidentally
 * reassigns a player's symbol mid-game.
 * - FAIL FAST: Constructor rejects Symbol.EMPTY immediately. A player
 * with no symbol makes no sense — better to fail at creation than
 * discover the bug hours later during gameplay.
 */
public class Player {

    private final String name;
    private final Symbol symbol;

    public Player(String name, Symbol symbol) {
        if (symbol == Symbol.EMPTY) {
            throw new IllegalArgumentException(
                    "Player symbol cannot be EMPTY. Use Symbol.X or Symbol.O.");
        }
        this.name = name;
        this.symbol = symbol;
    }

    public String getName() {
        return name;
    }

    public Symbol getSymbol() {
        return symbol;
    }

    @Override
    public String toString() {
        return name + " (" + symbol + ")";
    }
}
