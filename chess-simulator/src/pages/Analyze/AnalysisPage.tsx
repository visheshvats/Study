import { useState, useEffect, useRef } from "react";
import ChessboardWrapper from "@/components/Board/ChessboardWrapper";
import GameControls from "@/components/Controls/GameControls";
import MoveList from "@/components/MoveList/MoveList";
import EvalBar from "@/components/EvalBar/EvalBar";
import { useChessGame } from "@/chess/rules/useChessGame";
import { StockfishEngine } from "@/chess/engine/stockfish";

export default function AnalyzePage() {
    const { state, makeMove, resetGame, undoMove } = useChessGame();
    const [engine, setEngine] = useState<StockfishEngine | null>(null);
    const [evalScore, setEvalScore] = useState("0.0");
    const [fenInput, setFenInput] = useState("");
    const [orientation, setOrientation] = useState<"white" | "black">("white");
    const evaluationTimeoutRef = useRef<number | null>(null);

    useEffect(() => {
        const sf = new StockfishEngine();
        setEngine(sf);

        sf.onMessage = (msg: string) => {
            if (msg.includes("score")) {
                // Parse evaluation from engine output
                const scoreMatch = msg.match(/score cp (-?\d+)/);
                const mateMatch = msg.match(/score mate (-?\d+)/);

                if (mateMatch) {
                    setEvalScore(`M${mateMatch[1]}`);
                } else if (scoreMatch) {
                    const cp = parseInt(scoreMatch[1]);
                    const score = (cp / 100).toFixed(1);
                    setEvalScore(score);
                }
            }
        };

        return () => sf.quit();
    }, []);

    useEffect(() => {
        if (engine) {
            // Debounce evaluation requests
            if (evaluationTimeoutRef.current) {
                clearTimeout(evaluationTimeoutRef.current);
            }

            evaluationTimeoutRef.current = setTimeout(() => {
                engine.evaluate(state.fen, 18);
            }, 300);
        }
    }, [state.fen, engine]);

    function loadFen() {
        if (fenInput.trim()) {
            resetGame(fenInput);
            setFenInput("");
        }
    }

    return (
        <div className="flex flex-col lg:flex-row gap-6 p-4 lg:p-8 h-full">
            {/* Left: Board + Controls */}
            <div className="flex gap-4 items-start">
                <EvalBar evaluation={evalScore} />
                <div className="flex flex-col gap-4">
                    <div className="w-[500px] h-[500px]">
                        <ChessboardWrapper
                            fen={state.fen}
                            onMove={(f, t) => makeMove({ from: f, to: t, promotion: "q" })}
                            orientation={orientation}
                        />
                    </div>
                    <GameControls
                        onReset={() => resetGame()}
                        onUndo={undoMove}
                        onFlip={() => setOrientation(o => o === "white" ? "black" : "white")}
                        canUndo={state.history.length > 0}
                    />
                </div>
            </div>

            {/* Right: Analysis Panel */}
            <div className="flex-1 max-w-md flex flex-col gap-4">
                <div className="bg-zinc-900 p-4 rounded-xl border border-zinc-700">
                    <h2 className="font-bold text-xl mb-4">Analysis Board</h2>

                    <div className="mb-4 p-3 bg-zinc-800 rounded-lg">
                        <div className="text-xs text-zinc-500 mb-1">Evaluation</div>
                        <div className="text-2xl font-bold font-mono">
                            {evalScore.startsWith("M") ? (
                                <span className={evalScore.includes("-") ? "text-red-500" : "text-green-500"}>
                                    {evalScore}
                                </span>
                            ) : (
                                <span className={parseFloat(evalScore) > 0 ? "text-green-500" : parseFloat(evalScore) < 0 ? "text-red-500" : "text-zinc-400"}>
                                    {parseFloat(evalScore) > 0 ? "+" : ""}{evalScore}
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="flex gap-2 mb-4">
                        <input
                            className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 flex-1 text-sm focus:outline-none focus:border-amber-600"
                            placeholder="Paste FEN here..."
                            value={fenInput}
                            onChange={(e) => setFenInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && loadFen()}
                        />
                        <button
                            onClick={loadFen}
                            className="bg-amber-600 hover:bg-amber-500 px-4 rounded text-sm font-bold transition"
                        >
                            Load
                        </button>
                    </div>

                    <MoveList history={state.history} />
                </div>
            </div>
        </div>
    );
}
