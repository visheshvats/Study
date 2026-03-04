# 🎮 Tic Tac Toe — LLD Study Guide

> **Source:** [AlgoMaster.io — Design Tic Tac Toe](https://algomaster.io/learn/lld/design-tic-tac-toe)
> **Difficulty:** Medium | **Patterns:** Strategy, Observer, Singleton, Facade

---

## 📁 Project Structure

```
lld-tic-tac-toe/
└── src/
    ├── Symbol.java                  ← Enum: X, O, EMPTY
    ├── GameStatus.java              ← Enum: IN_PROGRESS, WINNER_X, WINNER_O, DRAW
    ├── InvalidMoveException.java    ← Custom RuntimeException
    ├── Player.java                  ← Data class (immutable)
    ├── Cell.java                    ← Data class (mutable)
    ├── WinningStrategy.java         ← Interface (Strategy pattern)
    ├── GameObserver.java            ← Interface (Observer pattern)
    ├── RowWinningStrategy.java      ← Strategy impl
    ├── ColumnWinningStrategy.java   ← Strategy impl
    ├── DiagonalWinningStrategy.java ← Strategy impl
    ├── Board.java                   ← Core: grid management
    ├── Game.java                    ← Core: orchestrator
    ├── Scoreboard.java              ← Core: Observer impl
    ├── TicTacToeSystem.java         ← Core: Singleton + Facade
    └── Demo.java                    ← Entry point
```

---

## 🗺️ Class Diagram (Simplified)

```
TicTacToeSystem (Singleton + Facade)
│
├── creates ──► Game
│               ├── has ──► Board ──► Cell[][]
│               ├── has ──► Player[] (X, O)
│               ├── uses ──► WinningStrategy[]
│               │            ├── RowWinningStrategy
│               │            ├── ColumnWinningStrategy
│               │            └── DiagonalWinningStrategy
│               └── notifies ──► GameObserver[]
│                                └── Scoreboard (implements GameObserver)
│
└── holds ──► Scoreboard (shared across games)
```

---

## 🧩 Entity Overview

| Category | Class | Key Traits |
|----------|-------|------------|
| **Enum** | `Symbol` | `X`, `O`, `EMPTY` — type-safe, display char |
| **Enum** | `GameStatus` | `IN_PROGRESS`, `WINNER_X`, `WINNER_O`, `DRAW` |
| **Exception** | `InvalidMoveException` | Extends `RuntimeException` |
| **Data** | `Player` | **Immutable** (`final` fields), fail-fast on `EMPTY` symbol |
| **Data** | `Cell` | **Mutable** — starts `EMPTY`, filled during play |
| **Interface** | `WinningStrategy` | `checkWin(board, row, col, symbol)` |
| **Interface** | `GameObserver` | `onGameEnd(game)` |
| **Core** | `Board` | Owns `Cell[][]`, single responsibility (no game rules) |
| **Core** | `Game` | Orchestrator, `synchronized makeMove()` |
| **Core** | `Scoreboard` | Implements `GameObserver`, `ConcurrentHashMap` |
| **Core** | `TicTacToeSystem` | Singleton + Facade, `volatile` + double-checked locking |

---

## 🎨 Design Patterns

### 1. Strategy Pattern — Win Detection

**Problem:** Win detection logic varies (row, column, diagonal). Hard-coding all three in `Game` violates Open/Closed Principle.

**Solution:** Extract each into a class implementing `WinningStrategy`.

```java
public interface WinningStrategy {
    boolean checkWin(Board board, int row, int col, Symbol symbol);
}
```

**Benefit:** Adding a new win condition (e.g., anti-diagonal only, or 4-in-a-row for a 4×4 board) = add a new class. **Zero changes to `Game`.**

```java
// In Game.java — strategy iteration
private boolean checkWin(int row, int col, Symbol symbol) {
    for (WinningStrategy strategy : winningStrategies) {
        if (strategy.checkWin(board, row, col, symbol)) return true;
    }
    return false;
}
```

---

### 2. Observer Pattern — Scoreboard Updates

**Problem:** `Game` shouldn't know about `Scoreboard`. Tight coupling makes it hard to add a Logger, UI updater, etc.

**Solution:** `Scoreboard` implements `GameObserver`. `Game` just calls `notifyObservers()`.

```java
public interface GameObserver {
    void onGameEnd(Game game);
}

// Scoreboard.java
@Override
public void onGameEnd(Game game) {
    Player winner = game.getWinner();
    if (winner != null) {
        scores.merge(winner.getName(), 1, Integer::sum); // atomic increment
    }
}
```

**Benefit:** Decoupled. `Game` doesn't know what observers do. Add a `Logger` observer without touching `Game`.

---

### 3. Singleton Pattern — TicTacToeSystem

**Problem:** The `Scoreboard` must persist across multiple games. Multiple instances would lose score history.

**Solution:** Singleton with **double-checked locking** + `volatile`.

```java
private static volatile TicTacToeSystem instance; // volatile is CRITICAL

public static TicTacToeSystem getInstance() {
    if (instance == null) {                    // 1st check: avoid lock cost
        synchronized (TicTacToeSystem.class) {
            if (instance == null) {            // 2nd check: handle race condition
                instance = new TicTacToeSystem();
            }
        }
    }
    return instance;
}
```

> **Why `volatile`?** Without it, instruction reordering could cause another thread to see a *partially constructed* object. `volatile` guarantees full visibility of the constructed instance.

---

### 4. Facade Pattern — TicTacToeSystem

**Problem:** External code shouldn't need to wire `Game`, `Board`, `Scoreboard`, and observers manually.

**Without Facade (verbose):**
```java
Board board = new Board(3);
Game game = new Game(alice, bob, 3);
Scoreboard sb = new Scoreboard();
game.addObserver(sb);
game.makeMove(0, 0);
```

**With Facade (clean):**
```java
TicTacToeSystem system = TicTacToeSystem.getInstance();
system.createGame(alice, bob);
system.makeMove(0, 0);
system.printScoreboard();
```

---

## ⚙️ `makeMove()` Flow

```
makeMove(row, col)
    │
    ├─ 1. status != IN_PROGRESS? → throw InvalidMoveException (fail fast)
    ├─ 2. cell not empty?        → throw InvalidMoveException
    ├─ 3. board.placeSymbol(row, col, symbol)
    ├─ 4. checkWin() → iterate all WinningStrategies
    │       └─ win found? → set status (WINNER_X / WINNER_O), notifyObservers(), return
    ├─ 5. board.isFull()?
    │       └─ yes → set status = DRAW, notifyObservers(), return
    └─ 6. switch currentPlayerIndex
```

---

## 🔑 Key Design Decisions & Rationale

| Decision | Why |
|----------|-----|
| `GameStatus.WINNER_X` / `WINNER_O` instead of `WINNER` + field | Simpler status checks; enum is self-contained |
| `Symbol.EMPTY` instead of `null` | Avoids `NullPointerException`; `isEmpty()` reads naturally |
| `Player` is immutable (`final` fields) | Prevents mid-game symbol reassignment bugs |
| `Cell` is mutable | Needs to change from `EMPTY` → `X`/`O` during play |
| `synchronized makeMove()` | Prevents race conditions in multi-threaded scenarios |
| `CopyOnWriteArrayList` for observers | Safe iteration even if observers are added during notification |
| `ConcurrentHashMap` + `merge()` in Scoreboard | Thread-safe atomic increment without explicit `synchronized` |
| `volatile` on singleton instance | Prevents partially-constructed object visibility across threads |
| `resetInstance()` on Singleton | Makes the singleton testable — reset between unit tests |
| Custom `InvalidMoveException` | Self-documenting API; cleaner than catching `RuntimeException` |

---

## 🧵 Thread Safety Summary

| Class | Mechanism | Why |
|-------|-----------|-----|
| `Game.makeMove()` | `synchronized` | Prevents concurrent moves corrupting state |
| `Game.observers` | `CopyOnWriteArrayList` | Safe iteration during notification |
| `Scoreboard.scores` | `ConcurrentHashMap` | Thread-safe map operations |
| `Scoreboard.onGameEnd()` | `merge()` | Atomic get-and-increment |
| `TicTacToeSystem.getInstance()` | `volatile` + double-checked locking | Safe lazy initialization |

---

## 🚀 How to Run

```bash
# From the lld-tic-tac-toe/ directory
javac src/*.java
java src.Demo
```

---

## 🧠 Interview Tips

1. **Start with requirements** — always ask about board size, player modes, scoreboard, move history before designing.

2. **Identify nouns → entities** — "grid" → `Board`, "square" → `Cell`, "player" → `Player`, "game state" → `GameStatus`.

3. **Justify your enums** — `Symbol.EMPTY` over `null`, `GameStatus.WINNER_X` over `WINNER + field`.

4. **Name the patterns explicitly** — interviewers want to hear "I'm using the Strategy pattern here because..."

5. **Thread safety is a bonus** — mentioning `synchronized`, `volatile`, `ConcurrentHashMap` shows senior-level thinking.

6. **Extensibility** — "If we needed a 4×4 board, I'd just add a new `WinningStrategy` — no changes to `Game`."

7. **Testability** — "I added `resetInstance()` to the Singleton so unit tests can run independently."

---

## 🔄 Possible Extensions (Follow-up Questions)

| Feature | Approach |
|---------|----------|
| AI opponent | Add `AIPlayer extends Player`, implement move selection strategy |
| Move history / Undo | Add a `Deque<Move>` to `Game`; `Move` stores `(row, col, player)` |
| 4×4 board | Pass `boardSize=4` to constructor; strategies already handle any size |
| Network multiplayer | Add a `MoveCommand` object; serialize over socket |
| Replay | Store `List<Move>` and replay by re-applying moves to a fresh board |
