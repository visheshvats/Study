
import ReactMarkdown from 'react-markdown';
import ChessboardWrapper from '@/components/Board/ChessboardWrapper';
import type { Lesson } from '@/types/curriculum';
import { ChevronLeft, ChevronRight, CheckCircle } from 'lucide-react';

interface LessonViewerProps {
    lesson: Lesson;
    isCompleted: boolean;
    onComplete: () => void;
    onNavigate: (direction: 'prev' | 'next') => void;
}

export default function LessonViewer({ lesson, isCompleted, onComplete, onNavigate }: LessonViewerProps) {
    return (
        <div className="max-w-4xl mx-auto p-6">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
                <div className="flex items-center gap-4 text-sm text-zinc-400">
                    <span>📚 {lesson.estimatedMinutes} minutes</span>
                    {isCompleted && (
                        <span className="flex items-center gap-1 text-green-500">
                            <CheckCircle size={16} />
                            Completed
                        </span>
                    )}
                </div>
            </div>

            {/* Lesson Content */}
            <div className="prose prose-invert max-w-none mb-8">
                <ReactMarkdown
                    components={{
                        h1: ({ children }) => <h2 className="text-2xl font-bold mt-8 mb-4">{children}</h2>,
                        h2: ({ children }) => <h3 className="text-xl font-bold mt-6 mb-3">{children}</h3>,
                        h3: ({ children }) => <h4 className="text-lg font-bold mt-4 mb-2">{children}</h4>,
                        p: ({ children }) => <p className="mb-4 text-zinc-300 leading-relaxed">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-2">{children}</ul>,
                        li: ({ children }) => <li className="text-zinc-300">{children}</li>,
                        strong: ({ children }) => <strong className="text-amber-400 font-bold">{children}</strong>,
                        code: ({ children }) => <code className="bg-zinc-800 px-2 py-1 rounded text-amber-400">{children}</code>,
                    }}
                >
                    {lesson.content}
                </ReactMarkdown>
            </div>

            {/* Position Diagrams */}
            {lesson.positions && lesson.positions.length > 0 && (
                <div className="mb-8">
                    <h3 className="text-xl font-bold mb-4">📊 Key Positions</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {lesson.positions.map((pos, idx) => (
                            <div key={idx} className="bg-zinc-900 p-4 rounded-xl border border-zinc-700">
                                <div className="mb-3">
                                    <ChessboardWrapper
                                        fen={pos.fen}
                                        onMove={() => { }}
                                        orientation={pos.orientation || 'white'}
                                        isDraggable={false}
                                    />
                                </div>
                                <p className="text-sm text-zinc-400">{pos.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Drills */}
            {lesson.drills && lesson.drills.length > 0 && (
                <div className="mb-8 bg-zinc-900 p-6 rounded-xl border border-zinc-700">
                    <h3 className="text-xl font-bold mb-4">🎯 Practice Drills</h3>
                    <ul className="space-y-3">
                        {lesson.drills.map((drill, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                                <span className="text-amber-500 font-bold">{idx + 1}.</span>
                                <span className="text-zinc-300">{drill}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between border-t border-zinc-700 pt-6">
                <button
                    onClick={() => onNavigate('prev')}
                    disabled={!lesson.prevLesson}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                    <ChevronLeft size={20} />
                    Previous Lesson
                </button>

                {!isCompleted && (
                    <button
                        onClick={onComplete}
                        className="px-6 py-2 rounded-lg bg-green-600 hover:bg-green-500 font-bold transition"
                    >
                        Mark as Complete
                    </button>
                )}

                <button
                    onClick={() => onNavigate('next')}
                    disabled={!lesson.nextLesson}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition font-bold"
                >
                    Next Lesson
                    <ChevronRight size={20} />
                </button>
            </div>
        </div>
    );
}
