package src;

/**
 * Represents the values a cell can contain.
 * Using an enum instead of raw characters provides type safety —
 * the compiler prevents invalid symbols at compile time.
 */
public enum Symbol {
    X('X'),
    O('O'),
    EMPTY('.');

    private final char displayChar;

    Symbol(char displayChar) {
        this.displayChar = displayChar;
    }

    public char getDisplayChar() {
        return displayChar;
    }

    @Override
    public String toString() {
        return String.valueOf(displayChar);
    }
}
