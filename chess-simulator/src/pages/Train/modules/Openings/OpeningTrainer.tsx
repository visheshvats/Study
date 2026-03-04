import { useState } from "react";
import ChessboardWrapper from "@/components/Board/ChessboardWrapper";
import { useChessGame } from "@/chess/rules/useChessGame";
import openingsData from "@/content/openings.json";

export default function OpeningTrainer() {
    const { game, state, makeMove, resetGame } = useChessGame();
    const [selectedOpening, setSelectedOpening] = useState(openingsData[0]);
    const [moveIndex, setMoveIndex] = useState(0);
    const [feedback, setFeedback] = useState("Make the first move!");

    function handleSelect(id: string) {
        const op = openingsData.find(o => o.id === id);
        if (op) {
            setSelectedOpening(op);
            setMoveIndex(0);
            resetGame();
            setFeedback("New line loaded.");
        }
    }

    function handleMove(from: string, to: string) {
        // Check if move matches the lines
        // Simplified: "moves" array is a sequence for BOTH players "e2e4", "e7e5", etc.
        // If it's my turn (playerColor), I must match the next move in array.
        // If it's opponent turn, they auto-move.

        // Actually, let's just enforce the sequence.
        const expectedMove = selectedOpening.moves[moveIndex];
        if (!expectedMove) {
            setFeedback("Line completed!");
            return;
        }

        const attempted = from + to;
        if (attempted === expectedMove) {
            makeMove({ from, to });
            setMoveIndex(i => i + 1);
            setFeedback("Correct!");

            // Auto-play next move if it exists
            setTimeout(() => {
                const nextMove = selectedOpening.moves[moveIndex + 1];
                if (nextMove) {
                    const f = nextMove.substring(0, 2);
                    const t = nextMove.substring(2, 4);
                    makeMove({ from: f, to: t });
                    setMoveIndex(i => i + 2); // Advanced 2 steps (user + opp)
                } else {
                    setFeedback("Line completed! Great job.");
                }
            }, 500);

        } else {
            setFeedback("Incorrect move. Try again.");
            makeMove({ from, to }); // Show it briefly then undo?
            setTimeout(() => {
                game.undo();
                resetGame(game.fen()); // Re-sync state
            }, 500);
        }
    }

    return (
        <div className="p-8 flex flex-col items-center gap-6">
            <h1 className="text-2xl font-bold">Opening Repertoire</h1>

            <select
                className="bg-zinc-800 p-2 rounded text-zinc-200"
                onChange={(e) => handleSelect(e.target.value)}
                value={selectedOpening.id}
            >
                {openingsData.map(o => (
                    <option key={o.id} value={o.id}>{o.name}</option>
                ))}
            </select>

            <div className="text-amber-500 font-mono text-lg">{feedback}</div>

            <ChessboardWrapper
                fen={state.fen}
                onMove={handleMove}
                orientation={selectedOpening.playerColor as any}
            />
        </div>
    );
}
