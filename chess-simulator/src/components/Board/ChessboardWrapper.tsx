import { Chessboard } from "react-chessboard";
import { useState, useEffect } from "react";
// import clsx from "clsx";

interface ChessboardWrapperProps {
    fen: string;
    onMove?: (from: string, to: string) => void;
    orientation?: "white" | "black";
    isDraggable?: boolean;
}

export default function ChessboardWrapper({
    fen,
    onMove,
    orientation = "white",
    isDraggable = true,
}: ChessboardWrapperProps) {
    const [boardWidth, setBoardWidth] = useState(400);

    useEffect(() => {
        // Simple responsive measuring
        const handleResize = () => {
            const container = document.getElementById("board-container");
            if (container) {
                setBoardWidth(Math.min(container.clientWidth, 600)); // Cap at 600px
            }
        };

        window.addEventListener("resize", handleResize);
        handleResize(); // Initial call
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    function onDrop(sourceSquare: string, targetSquare: string) {
        if (onMove) {
            onMove(sourceSquare, targetSquare);
            return true;
        }
        return false;
    }

    return (
        <div id="board-container" className="w-full aspect-square max-w-[600px] flex justify-center items-center">
            <Chessboard
                position={fen}
                onPieceDrop={onDrop}
                boardOrientation={orientation}
                arePiecesDraggable={isDraggable}
                autoPromoteToQueen // For now, we update later with modal
                boardWidth={boardWidth}
                customDarkSquareStyle={{ backgroundColor: "#8B5A2B" }}
                customLightSquareStyle={{ backgroundColor: "#D0C4B4" }}
            />
        </div>
    );
}
