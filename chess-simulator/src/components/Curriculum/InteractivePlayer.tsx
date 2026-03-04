import { useEffect } from 'react';
import { Chessboard } from 'react-chessboard';
import type { Square } from 'react-chessboard/dist/chessboard/types';
import { useInteractiveTraining } from '@/hooks/useInteractiveTraining';
import type { InteractiveLesson } from '@/types/interactive';
import {
    Lightbulb,
    RotateCcw,
    CheckCircle,
    XCircle,
    ArrowLeft,
    Trophy,
    Target
} from 'lucide-react';

interface InteractivePlayerProps {
    lesson: InteractiveLesson;
    onComplete: (result: { mistakes: number; hintsUsed: number }) => void;
    onBack: () => void;
}

export default function InteractivePlayer({ lesson, onComplete, onBack }: InteractivePlayerProps) {
    const {
        state,
        startLesson,
        makeMove,
        requestHint,
        resetLesson,
        getResult,
        getCurrentStep
    } = useInteractiveTraining();

    // Start lesson on mount
    useEffect(() => {
        startLesson(lesson);
    }, [lesson, startLesson]);

    // Handle completion
    useEffect(() => {
        if (state.status === 'completed') {
            const result = getResult();
            if (result) {
                onComplete({ mistakes: result.mistakes, hintsUsed: result.hintsUsed });
            }
        }
    }, [state.status, getResult, onComplete]);

    const currentStep = getCurrentStep();
    const progress = state.lesson
        ? ((state.currentStep + 1) / state.lesson.steps.length) * 100
        : 0;

    // Handle piece drop
    const handlePieceDrop = (sourceSquare: string, targetSquare: string) => {
        if (!state.isPlayerTurn || state.isComputerThinking) {
            return false;
        }
        return makeMove(sourceSquare, targetSquare);
    };

    // Get custom square styles for highlights
    const getCustomSquareStyles = () => {
        const styles: Record<string, React.CSSProperties> = {};

        if (currentStep?.highlight) {
            currentStep.highlight.forEach((square: string) => {
                styles[square] = {
                    backgroundColor: 'rgba(255, 200, 0, 0.4)',
                };
            });
        }

        return styles;
    };

    // Get custom arrows - use tuple format for react-chessboard
    const getCustomArrows = (): [Square, Square, string?][] => {
        if (!currentStep?.arrows) return [];
        return currentStep.arrows.map(arrow => [
            arrow.from as Square,
            arrow.to as Square,
            arrow.color || 'rgb(255, 170, 0)'
        ] as [Square, Square, string?]);
    };

    return (
        <div className="max-w-4xl mx-auto p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-zinc-400 hover:text-white transition"
                >
                    <ArrowLeft size={20} />
                    Back to Practice
                </button>
                <div className="flex items-center gap-2">
                    <Target size={18} className="text-amber-500" />
                    <span className="text-sm text-zinc-400">
                        {lesson.mode === 'guided' && 'Guided Tutorial'}
                        {lesson.mode === 'practice' && 'Practice Mode'}
                        {lesson.mode === 'puzzle' && 'Puzzle'}
                        {lesson.mode === 'freeplay' && 'Free Play'}
                    </span>
                </div>
            </div>

            {/* Title */}
            <div className="text-center mb-4">
                <h2 className="text-2xl font-bold">{lesson.title}</h2>
                <p className="text-zinc-400 text-sm">{lesson.description}</p>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
                <div className="flex justify-between text-sm text-zinc-400 mb-1">
                    <span>Step {state.currentStep + 1} of {state.lesson?.steps.length || 0}</span>
                    <span>{Math.round(progress)}% Complete</span>
                </div>
                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-300"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Chessboard */}
                <div className="flex justify-center">
                    <div className="w-full max-w-[400px]">
                        <Chessboard
                            position={state.currentFen}
                            onPieceDrop={handlePieceDrop}
                            boardOrientation={lesson.playerColor}
                            arePiecesDraggable={state.isPlayerTurn && !state.isComputerThinking}
                            customSquareStyles={getCustomSquareStyles()}
                            customArrows={getCustomArrows()}
                            boardWidth={400}
                            customDarkSquareStyle={{ backgroundColor: '#8B5A2B' }}
                            customLightSquareStyle={{ backgroundColor: '#D0C4B4' }}
                        />
                    </div>
                </div>

                {/* Instructions Panel */}
                <div className="space-y-4">
                    {/* Current Instruction */}
                    <div className="bg-zinc-900 rounded-xl p-5 border border-zinc-700">
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-xl">📝</span>
                            <span className="font-bold">Your Task</span>
                        </div>

                        {state.status === 'completed' ? (
                            <div className="text-center py-4">
                                <Trophy size={48} className="mx-auto text-amber-500 mb-3" />
                                <p className="text-xl font-bold text-green-400 mb-2">
                                    {lesson.successMessage}
                                </p>
                                <p className="text-zinc-400 text-sm">
                                    Mistakes: {state.mistakes} | Hints used: {state.hintsUsed}
                                </p>
                            </div>
                        ) : state.isComputerThinking ? (
                            <div className="text-center py-4">
                                <div className="animate-pulse text-amber-400">
                                    ♟️ Computer is thinking...
                                </div>
                            </div>
                        ) : currentStep ? (
                            <p className="text-zinc-200 leading-relaxed">
                                {currentStep.instruction}
                            </p>
                        ) : null}
                    </div>

                    {/* Feedback */}
                    {state.feedback && state.status !== 'completed' && (
                        <div className={`rounded-xl p-4 flex items-start gap-3 ${state.feedbackType === 'correct'
                                ? 'bg-green-900/30 border border-green-700'
                                : 'bg-red-900/30 border border-red-700'
                            }`}>
                            {state.feedbackType === 'correct' ? (
                                <CheckCircle size={20} className="text-green-400 mt-0.5 flex-shrink-0" />
                            ) : (
                                <XCircle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
                            )}
                            <p className={state.feedbackType === 'correct' ? 'text-green-300' : 'text-red-300'}>
                                {state.feedback}
                            </p>
                        </div>
                    )}

                    {/* Hint */}
                    {state.currentHint && (
                        <div className="bg-amber-900/30 border border-amber-700 rounded-xl p-4 flex items-start gap-3">
                            <Lightbulb size={20} className="text-amber-400 mt-0.5 flex-shrink-0" />
                            <p className="text-amber-300">{state.currentHint}</p>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                        {state.status !== 'completed' && (
                            <button
                                onClick={requestHint}
                                disabled={state.isComputerThinking}
                                className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
                            >
                                <Lightbulb size={18} />
                                Hint ({state.hintsUsed})
                            </button>
                        )}

                        <button
                            onClick={resetLesson}
                            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-zinc-700 hover:bg-zinc-600 transition font-medium"
                        >
                            <RotateCcw size={18} />
                            {state.status === 'completed' ? 'Try Again' : 'Reset'}
                        </button>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="bg-zinc-800 rounded-lg p-3 text-center">
                            <div className="text-2xl font-bold text-red-400">{state.mistakes}</div>
                            <div className="text-zinc-500">Mistakes</div>
                        </div>
                        <div className="bg-zinc-800 rounded-lg p-3 text-center">
                            <div className="text-2xl font-bold text-amber-400">{state.hintsUsed}</div>
                            <div className="text-zinc-500">Hints Used</div>
                        </div>
                    </div>

                    {/* Move History */}
                    {state.moveHistory.length > 0 && (
                        <div className="bg-zinc-800 rounded-lg p-3">
                            <div className="text-sm text-zinc-400 mb-2">Moves:</div>
                            <div className="flex flex-wrap gap-2">
                                {state.moveHistory.map((move: string, i: number) => (
                                    <span
                                        key={i}
                                        className={`px-2 py-1 rounded text-sm ${i % 2 === 0 ? 'bg-zinc-700' : 'bg-zinc-600'
                                            }`}
                                    >
                                        {Math.floor(i / 2) + 1}{i % 2 === 0 ? '.' : '...'} {move}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
