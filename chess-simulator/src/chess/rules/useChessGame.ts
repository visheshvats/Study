import { useState, useCallback, useRef } from "react";
import { Chess, Move } from "chess.js";

export interface GameState {
    fen: string;
    turn: "w" | "b";
    isCheck: boolean;
    isCheckmate: boolean;
    isStalemate: boolean;
    isDraw: boolean;
    isGameOver: boolean;
    history: string[]; // SAN moves
    captured: { w: string[]; b: string[] };
}

export function useChessGame(initialFen?: string) {
    const gameRef = useRef(new Chess(initialFen));
    const [state, setState] = useState<GameState>(() => {
        const game = gameRef.current;
        return {
            fen: game.fen(),
            turn: game.turn() as "w" | "b",
            isCheck: game.isCheck(),
            isCheckmate: game.isCheckmate(),
            isStalemate: game.isStalemate(),
            isDraw: game.isDraw(),
            isGameOver: game.isGameOver(),
            history: game.history(),
            captured: { w: [], b: [] },
        };
    });

    const getCapturedPieces = useCallback((history: Move[]) => {
        const captured = { w: [] as string[], b: [] as string[] };
        history.forEach(move => {
            if (move.captured) {
                // If white moved and captured, they captured a black piece
                if (move.color === 'w') captured.w.push(move.captured);
                else captured.b.push(move.captured);
            }
        });
        return captured;
    }, []);

    const updateState = useCallback(() => {
        const game = gameRef.current;
        setState({
            fen: game.fen(),
            turn: game.turn() as "w" | "b",
            isCheck: game.isCheck(),
            isCheckmate: game.isCheckmate(),
            isStalemate: game.isStalemate(),
            isDraw: game.isDraw(),
            isGameOver: game.isGameOver(),
            history: game.history(),
            captured: getCapturedPieces(game.history({ verbose: true })),
        });
    }, [getCapturedPieces]);

    const makeMove = useCallback((move: string | { from: string; to: string; promotion?: string }) => {
        try {
            const result = gameRef.current.move(move);
            updateState();
            return result;
        } catch (e) {
            console.error("Invalid move:", e);
            return null;
        }
    }, [updateState]);

    const resetGame = useCallback((fen?: string) => {
        gameRef.current = new Chess(fen);
        updateState();
    }, [updateState]);

    const undoMove = useCallback(() => {
        const result = gameRef.current.undo();
        if (result) {
            updateState();
        }
        return result;
    }, [updateState]);

    return {
        game: gameRef.current,
        state,
        makeMove,
        resetGame,
        undoMove,
    };
}
