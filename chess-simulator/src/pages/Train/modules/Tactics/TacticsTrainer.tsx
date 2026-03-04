import { useState, useEffect } from "react";
import ChessboardWrapper from "@/components/Board/ChessboardWrapper";
import { useChessGame } from "@/chess/rules/useChessGame";
import puzzlesData from "@/content/puzzles.json";

export default function TacticsTrainer() {
    const { game, state, makeMove, resetGame } = useChessGame();
    const [currentPuzzleIndex, setCurrentPuzzleIndex] = useState(0);
    const [status, setStatus] = useState<"solving" | "success" | "fail">("solving");

    const puzzle = puzzlesData[currentPuzzleIndex];

    useEffect(() => {
        if (puzzle) {
            resetGame(puzzle.fen);
            setStatus("solving");
        }
    }, [puzzle, resetGame]);

    function handleMove(from: string, to: string) {
        if (status !== "solving") return;

        // Check if move matches solution
        // Solution in JSON is e.g. "h5f7" (uci)
        // We need to verify if the move matches the next move in solution array
        // This is a simplified checker. Real one needs to track solution steps.

        // For this demo, let's assume solutionMoves[0] is the correct move for the USER.
        // If user is sideToMove.

        const attemptedMoveUci = from + to;
        // Note: promotion not handled in UCI string generation here properly without logic, 
        // but simplified for purpose.

        const correctMove = puzzle.solutionMoves[0]; // Simplified: just check first move for now.

        if (attemptedMoveUci === correctMove || (puzzle.solutionMoves.length > 0 && attemptedMoveUci === puzzle.solutionMoves[0])) {
            makeMove({ from, to, promotion: 'q' });
            setStatus("success");
        } else {
            makeMove({ from, to, promotion: 'q' }); // Allow wrong move to show it on board
            setStatus("fail");
            // Undo after delay
            setTimeout(() => {
                game.undo();
                resetGame(game.fen());
            }, 1000);
        }
    }

    function nextPuzzle() {
        setCurrentPuzzleIndex((i) => (i + 1) % puzzlesData.length);
    }

    return (
        <div className="flex flex-col items-center p-8 gap-4">
            <h1 className="text-2xl font-bold">Tactics Trainer</h1>
            <div className="text-zinc-400">Puzzle #{puzzle.id} • {puzzle.difficulty} • {puzzle.goal}</div>

            <div className="relative">
                <ChessboardWrapper
                    fen={state.fen}
                    onMove={handleBoardMove}
                    orientation={puzzle.sideToMove === 'w' ? 'white' : 'black'}
                    isDraggable={status === "solving"}
                />
                {status === "success" && (
                    <div className="absolute inset-0 bg-green-500/20 flex items-center justify-center pointer-events-none">
                        <div className="bg-green-600 text-white px-6 py-3 rounded-xl font-bold text-2xl animate-bounce">
                            Correct!
                        </div>
                    </div>
                )}
                {status === "fail" && (
                    <div className="absolute inset-0 bg-red-500/20 flex items-center justify-center pointer-events-none">
                        <div className="bg-red-600 text-white px-6 py-3 rounded-xl font-bold text-2xl">
                            Incorrect
                        </div>
                    </div>
                )}
            </div>

            <div className="flex gap-4">
                <button onClick={() => resetGame(puzzle.fen)} className="text-zinc-400 hover:text-white">Retry</button>
                <button
                    onClick={nextPuzzle}
                    className="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-bold"
                >
                    Next Puzzle
                </button>
            </div>
        </div>
    );

    function handleBoardMove(from: string, to: string) {
        handleMove(from, to);
    }
}
