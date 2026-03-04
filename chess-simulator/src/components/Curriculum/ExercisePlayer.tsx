import { useState } from 'react';
import ChessboardWrapper from '@/components/Board/ChessboardWrapper';
import type { Exercise, ExerciseResult } from '@/types/curriculum';
import { CheckCircle, XCircle, Lightbulb, RotateCcw } from 'lucide-react';

interface ExercisePlayerProps {
    exercise: Exercise;
    onComplete: (result: ExerciseResult) => void;
}

export default function ExercisePlayer({ exercise, onComplete }: ExercisePlayerProps) {
    const [selectedAnswer, setSelectedAnswer] = useState<string>('');
    const [userInput, setUserInput] = useState<string>('');
    const [submitted, setSubmitted] = useState(false);
    const [isCorrect, setIsCorrect] = useState(false);
    const [attempts, setAttempts] = useState(0);
    const [showHint, setShowHint] = useState(false);
    const [startTime] = useState(Date.now());

    const handleSubmit = () => {
        const answer = exercise.type === 'notation' || exercise.type === 'text' ? userInput.trim() : selectedAnswer;
        const correct = checkAnswer(answer);

        setSubmitted(true);
        setIsCorrect(correct);
        setAttempts(prev => prev + 1);

        if (correct) {
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);
            onComplete({
                exerciseId: exercise.id,
                correct: true,
                attempts: attempts + 1,
                timestamp: new Date(),
                timeSpent,
            });
        }
    };

    const checkAnswer = (answer: string): boolean => {
        if (Array.isArray(exercise.correctAnswer)) {
            return exercise.correctAnswer.some(ca =>
                ca.toLowerCase().trim() === answer.toLowerCase().trim()
            );
        }
        return exercise.correctAnswer.toLowerCase().trim() === answer.toLowerCase().trim();
    };

    const handleRetry = () => {
        setSubmitted(false);
        setSelectedAnswer('');
        setUserInput('');
        setShowHint(false);
    };

    const renderExerciseInput = () => {
        switch (exercise.type) {
            case 'multiple-choice':
                return (
                    <div className="space-y-3">
                        {exercise.options?.map((option, idx) => (
                            <button
                                key={idx}
                                onClick={() => !submitted && setSelectedAnswer(option)}
                                disabled={submitted}
                                className={`w-full p-4 rounded-lg border-2 text-left transition ${selectedAnswer === option
                                    ? 'border-amber-500 bg-amber-500/10'
                                    : 'border-zinc-700 hover:border-zinc-600'
                                    } ${submitted ? 'cursor-not-allowed opacity-75' : 'cursor-pointer'}`}
                            >
                                <span className="font-bold mr-3">{String.fromCharCode(65 + idx)}.</span>
                                {option}
                            </button>
                        ))}
                    </div>
                );

            case 'notation':
            case 'text':
                return (
                    <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && !submitted && handleSubmit()}
                        disabled={submitted}
                        placeholder="Type your answer..."
                        className="w-full p-4 rounded-lg bg-zinc-800 border-2 border-zinc-700 focus:border-amber-500 focus:outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                    />
                );

            case 'position':
                return (
                    <div className="space-y-4">
                        {exercise.fen && (
                            <div className="flex justify-center mb-4">
                                <div className="w-[400px]">
                                    <ChessboardWrapper
                                        fen={exercise.fen}
                                        onMove={() => { }}
                                        isDraggable={false}
                                    />
                                </div>
                            </div>
                        )}
                        <div className="space-y-3">
                            {exercise.options?.map((option, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => !submitted && setSelectedAnswer(option)}
                                    disabled={submitted}
                                    className={`w-full p-4 rounded-lg border-2 text-left transition ${selectedAnswer === option
                                        ? 'border-amber-500 bg-amber-500/10'
                                        : 'border-zinc-700 hover:border-zinc-600'
                                        } ${submitted ? 'cursor-not-allowed opacity-75' : 'cursor-pointer'}`}
                                >
                                    <span className="font-bold mr-3">{String.fromCharCode(65 + idx)}.</span>
                                    {option}
                                </button>
                            ))}
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="max-w-3xl mx-auto p-6">
            {/* Exercise Header */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm text-zinc-500">
                        {exercise.type.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </span>
                    <span className="text-sm text-zinc-500">•</span>
                    <span className="text-sm text-zinc-500">
                        Difficulty: {'⭐'.repeat(exercise.difficulty)}
                    </span>
                </div>
                <h2 className="text-2xl font-bold">{exercise.question}</h2>
            </div>

            {/* Exercise Input */}
            <div className="mb-6">
                {renderExerciseInput()}
            </div>

            {/* Hints */}
            {exercise.hints && exercise.hints.length > 0 && !submitted && (
                <div className="mb-6">
                    <button
                        onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-2 text-amber-500 hover:text-amber-400 transition"
                    >
                        <Lightbulb size={20} />
                        {showHint ? 'Hide Hint' : 'Show Hint'}
                    </button>
                    {showHint && (
                        <div className="mt-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                            <p className="text-sm text-amber-200">{exercise.hints[0]}</p>
                        </div>
                    )}
                </div>
            )}

            {/* Feedback */}
            {submitted && (
                <div className={`mb-6 p-6 rounded-xl border-2 ${isCorrect
                    ? 'bg-green-500/10 border-green-500'
                    : 'bg-red-500/10 border-red-500'
                    }`}>
                    <div className="flex items-start gap-3 mb-3">
                        {isCorrect ? (
                            <CheckCircle className="text-green-500 flex-shrink-0" size={24} />
                        ) : (
                            <XCircle className="text-red-500 flex-shrink-0" size={24} />
                        )}
                        <div>
                            <h3 className="font-bold text-lg mb-2">
                                {isCorrect ? 'Correct!' : 'Not quite right'}
                            </h3>
                            <p className="text-zinc-300">{exercise.explanation}</p>
                            {!isCorrect && (
                                <p className="mt-2 text-sm text-zinc-400">
                                    Correct answer: <span className="font-bold text-white">{exercise.correctAnswer}</span>
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
                {!submitted ? (
                    <button
                        onClick={handleSubmit}
                        disabled={!selectedAnswer && !userInput}
                        className="flex-1 py-3 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed font-bold transition"
                    >
                        Submit Answer
                    </button>
                ) : !isCorrect ? (
                    <button
                        onClick={handleRetry}
                        className="flex-1 py-3 rounded-lg bg-zinc-700 hover:bg-zinc-600 font-bold transition flex items-center justify-center gap-2"
                    >
                        <RotateCcw size={20} />
                        Try Again
                    </button>
                ) : null}
            </div>
        </div>
    );
}
