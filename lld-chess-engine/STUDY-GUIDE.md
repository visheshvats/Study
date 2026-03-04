# ♔ Chess Engine — LLD Study Guide

> **Style:** Low-Level Design (OOP) • **Language:** Java 17+
> **Patterns:** Strategy, Observer, Command, Factory, Builder

---

## 📁 Project Structure

```
lld-chess-engine/
└── src/
    ├── enums/
    │   ├── Color.java              ← WHITE / BLACK
    │   ├── PieceType.java          ← KING, QUEEN, … with symbols + values
    │   └── GameStatus.java         ← ACTIVE, WHITE_WINS, BLACK_WINS, STALEMATE, DRAW
    ├── core/
    │   ├── Position.java           ← Immutable (row, col) ↔ algebraic "e4"
    │   └── Move.java               ← Immutable command object (Builder pattern)
    ├── pieces/
    │   ├── Piece.java              ← Abstract base (Strategy pattern)
    │   ├── King.java               ← 8-direction, 1 square
    │   ├── Queen.java              ← 8-direction sliding
    │   ├── Rook.java               ← 4-direction straight sliding
    │   ├── Bishop.java             ← 4-direction diagonal sliding
    │   ├── Knight.java             ← L-shaped jumps
    │   ├── Pawn.java               ← Forward + diagonal capture + double push
    │   ├── SlidingPieceHelper.java ← DRY helper for Q/R/B
    │   └── PieceFactory.java       ← Factory + FEN char conversion
    ├── board/
    │   └── Board.java              ← 8×8 grid, FEN I/O, attack detection
    ├── game/
    │   ├── Game.java               ← Orchestrator (rules, turns, check/mate)
    │   ├── GameObserver.java       ← Observer interface
    │   └── MoveLogger.java         ← Console logging observer
    └── Demo.java                   ← Entry point (4 scenarios)
```

---

## 🎨 Design Patterns

### 1. Strategy Pattern — Piece Movement

Each piece subclass encapsulates its own movement logic. The Game calls `piece.getPseudoLegalMoves()` polymorphically — no switch statements.

```java
// Game doesn't know HOW pieces move — it just asks
Piece piece = board.getPieceAt(position);
List<Position> moves = piece.getPseudoLegalMoves(position, board);
```

**Benefit:** Adding a new piece type (e.g., "Empress" in fairy chess) = new subclass. Zero changes to Game or Board.

---

### 2. Command Pattern — Move / Undo

Each `Move` is an immutable command object that stores enough state for full reversal:

```java
// Execute
moveHistory.push(move);
executeMove(move);

// Undo — restores captured piece, first-move flags, everything
Move move = moveHistory.pop();
// ... reverse all state changes
```

**Key fields:** `from`, `to`, `movedPiece`, `capturedPiece`, `isFirstMove`, `isCastling`, `isEnPassant`, `promotionType`

---

### 3. Observer Pattern — Game Events

```java
game.addObserver(new MoveLogger());   // logs moves
game.addObserver(new PGNRecorder());  // could record to file
```

Game notifies observers on: `onMoveMade()`, `onGameEnd()`, `onMoveUndone()`.

---

### 4. Factory Pattern — Piece Creation

```java
Piece queen = PieceFactory.create(PieceType.QUEEN, Color.WHITE);
Piece fromFen = PieceFactory.fromFenChar('n'); // → Black Knight
```

FEN parsing uses the factory to reconstruct any position.

---

### 5. Builder Pattern — Move Construction

```java
Move move = new Move.Builder(from, to, piece)
    .capturedPiece(captured)
    .castling()
    .firstMove(true)
    .build();
```

Clean API for moves with many optional flags.

---

## ♟️ Chess Rules Implemented

| Rule | Where | How |
|------|-------|-----|
| **Piece movement** | Each `Piece` subclass | `getPseudoLegalMoves()` |
| **Check detection** | `Board.isSquareAttacked()` | Checks if King's square is attacked |
| **Legal move filtering** | `Game.leavesKingInCheck()` | Simulates move, checks King safety, undoes |
| **Checkmate** | `Game.updateGameStatus()` | No legal moves + in check |
| **Stalemate** | `Game.updateGameStatus()` | No legal moves + NOT in check |
| **Castling** | `Game.addCastlingMoves()` | King/Rook unmoved, path clear, not through check |
| **En passant** | `Game.getLegalMovesForPiece()` | Tracks `enPassantTarget` from double-push |
| **Pawn promotion** | `Game.makeMove()` | Auto-queens or accepts custom promotion type |
| **Insufficient material** | `Game.isInsufficientMaterial()` | K vs K, K+B vs K, K+N vs K |

---

## ⚙️ `makeMove()` Flow

```
makeMove("e2", "e4")
  │
  ├─ 1. status.isTerminal()?  → reject
  ├─ 2. piece at "e2"?       → null check
  ├─ 3. correct turn?        → color check
  ├─ 4. getLegalMovesForPiece("e2")
  │       ├─ piece.getPseudoLegalMoves()    ← Strategy
  │       ├─ filter: leavesKingInCheck()    ← simulate & undo
  │       ├─ add en passant moves
  │       └─ add castling moves (King only)
  ├─ 5. find matching target "e4"
  ├─ 6. executeMove(move)                  ← apply to board
  ├─ 7. moveHistory.push(move)             ← Command
  ├─ 8. updateEnPassantTarget()
  ├─ 9. notifyMoveMade(move)               ← Observer
  ├─ 10. switch turn
  └─ 11. updateGameStatus()
           ├─ getAllLegalMoves() for opponent
           ├─ if empty + in check → CHECKMATE
           ├─ if empty + safe     → STALEMATE
           └─ isInsufficientMaterial() → DRAW
```

---

## 🔑 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `Piece[][]` instead of `Cell` wrapper | Direct piece access simplifies move gen |
| Pseudo-legal → legal filtering | Simpler than computing pins/checks during generation |
| `Position` is immutable | Shared references can't cause mutation bugs |
| `Move` uses Builder pattern | Many optional flags (castling, EP, promotion) |
| `SlidingPieceHelper` extracted | DRY — Q/R/B share identical slide logic |
| Castling in `Game`, not `King` | Requires multi-piece coordination + attack checks |
| En passant in `Game`, not `Pawn` | Requires context from opponent's last move |
| `CopyOnWriteArrayList` for observers | Thread-safe notification iteration |

---

## 🚀 How to Run

```bash
cd lld-chess-engine
javac src/enums/*.java src/core/*.java src/pieces/*.java src/board/*.java src/game/*.java src/Demo.java
java src.Demo
```

---

## 🧠 Interview Tips

1. **Start with entities** — Board, Piece, Move, Game. Interviewers want to see you decompose.
2. **Name your patterns** — "I'm using Strategy for piece movement because..."
3. **Explain legal vs pseudo-legal** — most candidates miss the distinction.
4. **Castling/en passant are differentiators** — handling them shows depth.
5. **Command pattern for undo** — shows senior-level thinking about reversibility.
6. **Thread safety** — mention `synchronized makeMove()` and why.
7. **Extensibility** — "Adding fairy chess pieces = new subclass, zero changes to Game."

---

## 🔄 Possible Extensions

| Feature | Approach |
|---------|----------|
| AI opponent | Minimax + alpha-beta pruning on `getAllLegalMoves()` |
| Move notation (SAN) | "Nf3", "O-O" from Move objects |
| PGN export | Observer that records moves in PGN format |
| Threefold repetition | Hash board state, track counts in a Map |
| Fifty-move rule | Counter in Game, reset on pawn move or capture |
| Time controls | `Clock` class with `Instant` tracking |
