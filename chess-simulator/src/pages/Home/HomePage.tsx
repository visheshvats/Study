import { Link } from "react-router-dom";
import { Gamepad2, GraduationCap } from "lucide-react";

export default function HomePage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] gap-8 p-4 text-center">
            <div className="flex flex-col items-center gap-4">
                <div className="w-24 h-24 bg-amber-600 rounded-2xl flex items-center justify-center text-6xl shadow-2xl skew-y-3">
                    ♔
                </div>
                <h1 className="text-5xl font-bold tracking-tighter bg-gradient-to-br from-white to-zinc-500 bg-clip-text text-transparent">
                    Chess Simulator
                </h1>
                <p className="text-xl text-zinc-400 max-w-md">
                    The ultimate offline-capable training and playing environment.
                </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 w-full max-w-lg">
                <Link
                    to="/play"
                    className="flex-1 bg-zinc-100 text-zinc-900 p-4 rounded-xl font-bold flex items-center justify-center gap-2 hover:scale-105 transition-transform"
                >
                    <Gamepad2 /> Play Now
                </Link>
                <Link
                    to="/train"
                    className="flex-1 bg-zinc-800 text-zinc-100 border border-zinc-700 p-4 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-zinc-700 transition"
                >
                    <GraduationCap /> Training Hub
                </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-2xl mt-8">
                <StatBox label="Puzzles Solved" value="0" />
                <StatBox label="Accuracy" value="-" />
                <StatBox label="Streak" value="0 Days" />
                <StatBox label="Rating" value="1200?" />
            </div>
        </div>
    );
}

function StatBox({ label, value }: { label: string, value: string }) {
    return (
        <div className="bg-zinc-900/50 p-4 rounded-lg border border-zinc-800">
            <div className="text-2xl font-bold text-white">{value}</div>
            <div className="text-xs text-zinc-500 uppercase tracking-widest">{label}</div>
        </div>
    );
}
