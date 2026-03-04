import { useState, useEffect } from "react";
import ChessboardWrapper from "@/components/Board/ChessboardWrapper";
import GameControls from "@/components/Controls/GameControls";
import MoveList from "@/components/MoveList/MoveList";
import GameOverModal from "@/components/Modals/GameOverModal";
import { useChessGame } from "@/chess/rules/useChessGame";
import { StockfishEngine } from "@/chess/engine/stockfish";

export default function PlayPage() {
    const { state, makeMove, resetGame, undoMove } = useChessGame();
    const [orientation, setOrientation] = useState<"white" | "black">("white");
    const [engine, setEngine] = useState<StockfishEngine | null>(null);
    const [playMode, setPlayMode] = useState<"HvH" | "HvC">("HvH");
    const [engineLevel, setEngineLevel] = useState(5); // 1-10
    const [computerThinking, setComputerThinking] = useState(false);

    // Initialize Engine
    useEffect(() => {
        const sf = new StockfishEngine();
        setEngine(sf);
        return () => sf.quit();
    }, []);

    // Computer Move Logic
    useEffect(() => {
        if (
            playMode === "HvC" &&
            state.turn === (orientation === "white" ? "b" : "w") &&
            !state.isGameOver &&
            engine &&
            !computerThinking
        ) {
            setComputerThinking(true);

            // Set skill level
            engine.setSkillLevel(engineLevel * 2); // Map 1-10 to 2-20

            // Set up message handler BEFORE sending command
            engine.onMessage = (msg: string) => {
                if (msg.startsWith("bestmove")) {
                    const parts = msg.split(" ");
                    const move = parts[1];

                    if (move && move !== "(none)") {
                        const from = move.substring(0, 2);
                        const to = move.substring(2, 4);
                        const promotion = move.length > 4 ? move.substring(4, 5) : undefined;

                        // Delay slightly for better UX
                        setTimeout(() => {
                            makeMove({ from, to, promotion });
                            setComputerThinking(false);
                        }, 300);
                    } else {
                        setComputerThinking(false);
                    }
                }
            };

            // Request best move
            engine.getBestMove(state.fen, 10);
        }
    }, [state.turn, state.fen, playMode, orientation, engine, state.isGameOver, computerThinking, makeMove, engineLevel]);

    function handleBoardMove(from: string, to: string) {
        if (playMode === "HvC" && computerThinking) return;

        // Make the move (auto-queen for now)
        makeMove({ from, to, promotion: "q" });
    }

    function handleReset() {
        setComputerThinking(false);
        resetGame();
    }

    return (
        <div className="flex flex-col lg:flex-row h-full gap-4 p-4 lg:p-8">
            {/* Left Column: Board */}
            <div className="flex-1 flex flex-col items-center justify-center min-h-[400px]">
                <ChessboardWrapper
                    fen={state.fen}
                    onMove={handleBoardMove}
                    orientation={orientation}
                    isDraggable={!state.isGameOver && (!computerThinking || playMode === "HvH")}
                />
                <div className="mt-4 w-full max-w-[600px]">
                    <GameControls
                        onReset={handleReset}
                        onUndo={undoMove}
                        onFlip={() => setOrientation((o) => (o === "white" ? "black" : "white"))}
                        canUndo={state.history.length > 0 && !computerThinking}
                    />
                </div>
            </div>

            {/* Right Column: Info & Settings */}
            <div className="w-full lg:w-80 flex flex-col gap-4">
                {/* Game Info Card */}
                <div className="bg-zinc-900 p-4 rounded-xl border border-zinc-700">
                    <h2 className="font-bold text-xl mb-4">Play</h2>

                    <div className="flex gap-2 mb-4 bg-zinc-800 p-1 rounded-lg">
                        <button
                            onClick={() => {
                                setPlayMode("HvH");
                                setComputerThinking(false);
                            }}
                            className={`flex-1 py-1 text-sm rounded ${playMode === "HvH" ? "bg-zinc-600 shadow" : "hover:bg-zinc-700"
                                }`}
                        >
                            Vs Friend
                        </button>
                        <button
                            onClick={() => setPlayMode("HvC")}
                            className={`flex-1 py-1 text-sm rounded ${playMode === "HvC" ? "bg-zinc-600 shadow" : "hover:bg-zinc-700"
                                }`}
                        >
                            Vs Computer
                        </button>
                    </div>

                    {playMode === "HvC" && (
                        <div className="mb-4">
                            <label className="text-xs text-zinc-400 mb-1 block">
                                Engine Level: {engineLevel}
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={engineLevel}
                                onChange={(e) => setEngineLevel(Number(e.target.value))}
                                className="w-full accent-amber-600"
                            />
                            <div className="flex justify-between text-xs text-zinc-500 mt-1">
                                <span>Beginner</span>
                                <span>Master</span>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-between text-sm text-zinc-400 mb-2">
                        <span>{state.turn === "w" ? "White" : "Black"} to move</span>
                        {state.isCheck && <span className="text-red-500 font-bold">CHECK!</span>}
                    </div>

                    {computerThinking && (
                        <div className="text-amber-500 text-sm animate-pulse">
                            Computer is thinking...
                        </div>
                    )}
                </div>

                {/* Move History */}
                <MoveList history={state.history} />
            </div>

            {/* Modals */}
            <GameOverModal
                isOpen={state.isGameOver}
                winner={
                    state.turn === "w"
                        ? state.isCheckmate
                            ? "black"
                            : "draw"
                        : state.isCheckmate
                            ? "white"
                            : "draw"
                }
                reason={state.isCheckmate ? "Checkmate" : "Draw"}
                onRematch={handleReset}
                onClose={() => { }}
            />
        </div>
    );
}
