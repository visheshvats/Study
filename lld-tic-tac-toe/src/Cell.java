package src;

/**
 * Represents a single cell on the board.
 *
 * Design decisions:
 * - MUTABLE: Unlike Player, Cell changes state during gameplay.
 * It starts as EMPTY and gets set to X or O when a player moves.
 * - isEmpty() helper: Makes calling code more readable.
 * "if (cell.isEmpty())" is clearer than "if (cell.getSymbol() == Symbol.EMPTY)"
 */
public class Cell {

    private Symbol symbol;

    public Cell() {
        this.symbol = Symbol.EMPTY;
    }

    public Symbol getSymbol() {
        return symbol;
    }

    public void setSymbol(Symbol symbol) {
        this.symbol = symbol;
    }

    public boolean isEmpty() {
        return this.symbol == Symbol.EMPTY;
    }
}
