import { useState } from "react";
import { Chessboard } from "react-chessboard";

export default function BasicsTrainer() {
    const [targetSquare, setTargetSquare] = useState(randomSquare());
    const [score, setScore] = useState(0);
    const [message, setMessage] = useState("Click on: " + targetSquare);

    function randomSquare() {
        const files = "abcdefgh";
        const ranks = "12345678";
        return files[Math.floor(Math.random() * 8)] + ranks[Math.floor(Math.random() * 8)];
    }

    function onSquareClick(square: string) {
        if (square === targetSquare) {
            setScore(s => s + 1);
            const next = randomSquare();
            setTargetSquare(next);
            setMessage("Correct! Next: " + next);
        } else {
            setScore(0);
            setMessage("Wrong! Try again. Find: " + targetSquare);
        }
    }

    return (
        <div className="p-8 flex flex-col items-center">
            <h1 className="text-2xl font-bold mb-4">Vision Trainer</h1>
            <p className="mb-4 text-xl text-amber-500 font-mono">{message}</p>
            <div className="text-sm text-zinc-500 mb-4">Streak: {score}</div>
            <div className="w-[400px] h-[400px]">
                <Chessboard
                    position="empty"
                    onSquareClick={onSquareClick}
                    boardWidth={400}
                />
            </div>
        </div>
    );
}
