# 03. Check, Checkmate, Stalemate

## Check (+)
The King is under attack. You MUST save the King immediately.
**Three ways to escape check (CPR):**
1.  **C**apture the attacker.
2.  **P**rotect (Block) the line of attack.
3.  **R**un away (Move the King).

## Checkmate (#)
The King is in check, and there is **NO** legal escape. The game is over. **You Win.**

### Example: Scholar's Mate
```
  8 | r n b q k b n r
  7 | p p p p . p p p
  6 | . . . . . . . .
  5 | . . B . . . . .
  4 | . . . . P . . .
  3 | . . . . . . . .
  2 | P P P P . Q P P
  1 | R N B . K . N R
    +----------------
      a b c d e f g h
```
White plays `Qxf7#`. The King cannot capture (protected by Bishop), cannot block, cannot run.

## Stalemate (Draw)
The King is **NOT** in check, but has **NO** legal moves. The game is a DRAW (1/2 point each).
- **Common Mistake**: When you are winning huge (Queen + Rook vs King), do not accidentally stalemate! Always give check or make sure the King has a breathing square.

## Other Draws
- **Insufficient Material**: K vs K, K+N vs K, K+B vs K (Cannot force mate).
- **3-Fold Repetition**: The exact same position occurs 3 times.
- **50-Move Rule**: No pawn move or capture for 50 moves.

## Drills
1.  Set up K vs Q+K. Try to checkmate the lone King. Avoid Stalemate.
2.  Find "Fool's Mate" (Fastest mate possible).
