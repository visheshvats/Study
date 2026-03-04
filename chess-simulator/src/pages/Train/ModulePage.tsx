import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LessonViewer from '@/components/Curriculum/LessonViewer';
import ExercisePlayer from '@/components/Curriculum/ExercisePlayer';
import InteractivePlayer from '@/components/Curriculum/InteractivePlayer';
import { useCurriculum } from '@/hooks/useCurriculum';
import type { Lesson, Exercise } from '@/types/curriculum';
import type { InteractiveLesson } from '@/types/interactive';
import { BookOpen, Trophy, ArrowLeft, Gamepad2 } from 'lucide-react';

export default function ModulePage() {
    const { moduleId } = useParams<{ moduleId: string }>();
    const navigate = useNavigate();
    const { progress, completeLesson, recordExerciseResult } = useCurriculum();

    const [lessons, setLessons] = useState<Lesson[]>([]);
    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [interactiveLessons, setInteractiveLessons] = useState<InteractiveLesson[]>([]);
    const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
    const [mode, setMode] = useState<'lessons' | 'exercises' | 'practice'>('lessons');
    const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
    const [currentInteractiveIndex, setCurrentInteractiveIndex] = useState(0);
    const [playingInteractive, setPlayingInteractive] = useState(false);
    const [loading, setLoading] = useState(true);

    // Load module content
    useEffect(() => {
        const loadModule = async () => {
            try {
                const lessonsData = await import(`@/content/curriculum/${moduleId}/lessons.json`);
                const exercisesData = await import(`@/content/curriculum/${moduleId}/exercises.json`);

                setLessons(lessonsData.lessons || []);
                setExercises(exercisesData.exercises || []);

                // Try to load interactive content (may not exist for all modules)
                try {
                    const interactiveData = await import(`@/content/curriculum/${moduleId}/interactive.json`);
                    setInteractiveLessons(interactiveData.lessons || []);
                } catch {
                    // No interactive content for this module
                    setInteractiveLessons([]);
                }

                setLoading(false);
            } catch (error) {
                console.error('Failed to load module:', error);
                setLoading(false);
            }
        };

        if (moduleId) {
            loadModule();
        }
    }, [moduleId]);

    const currentLesson = lessons[currentLessonIndex];
    const currentExercise = exercises[currentExerciseIndex];
    const currentInteractive = interactiveLessons[currentInteractiveIndex];

    const handleLessonComplete = () => {
        if (currentLesson) {
            completeLesson(currentLesson.id);
        }
    };

    const handleLessonNavigate = (direction: 'prev' | 'next') => {
        if (direction === 'next' && currentLessonIndex < lessons.length - 1) {
            setCurrentLessonIndex(prev => prev + 1);
        } else if (direction === 'prev' && currentLessonIndex > 0) {
            setCurrentLessonIndex(prev => prev - 1);
        }
    };

    const handleExerciseComplete = (result: any) => {
        recordExerciseResult(result);

        // Move to next exercise after a delay
        setTimeout(() => {
            if (currentExerciseIndex < exercises.length - 1) {
                setCurrentExerciseIndex(prev => prev + 1);
            }
        }, 1500);
    };

    const handleInteractiveComplete = useCallback((result: { mistakes: number; hintsUsed: number }) => {
        console.log('Interactive completed:', result);
        // Could save results here
        setPlayingInteractive(false);

        // Move to next if available
        if (currentInteractiveIndex < interactiveLessons.length - 1) {
            setCurrentInteractiveIndex(prev => prev + 1);
        }
    }, [currentInteractiveIndex, interactiveLessons.length]);

    const startInteractive = (index: number) => {
        setCurrentInteractiveIndex(index);
        setPlayingInteractive(true);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
                    <p className="text-zinc-400">Loading module...</p>
                </div>
            </div>
        );
    }

    // If playing interactive, show full-screen interactive player
    if (playingInteractive && currentInteractive) {
        return (
            <div className="min-h-screen bg-zinc-950">
                <InteractivePlayer
                    lesson={currentInteractive}
                    onComplete={handleInteractiveComplete}
                    onBack={() => setPlayingInteractive(false)}
                />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950">
            {/* Header */}
            <div className="bg-zinc-900 border-b border-zinc-800 sticky top-0 z-10">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => navigate('/train')}
                            className="flex items-center gap-2 text-zinc-400 hover:text-white transition"
                        >
                            <ArrowLeft size={20} />
                            Back to Training
                        </button>

                        <div className="flex gap-2">
                            <button
                                onClick={() => setMode('lessons')}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${mode === 'lessons'
                                    ? 'bg-amber-600 text-white'
                                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                                    }`}
                            >
                                <BookOpen size={18} />
                                Lessons ({lessons.length})
                            </button>
                            <button
                                onClick={() => setMode('exercises')}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${mode === 'exercises'
                                    ? 'bg-amber-600 text-white'
                                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                                    }`}
                            >
                                <Trophy size={18} />
                                Exercises ({exercises.length})
                            </button>
                            {interactiveLessons.length > 0 && (
                                <button
                                    onClick={() => setMode('practice')}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${mode === 'practice'
                                        ? 'bg-green-600 text-white'
                                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                                        }`}
                                >
                                    <Gamepad2 size={18} />
                                    Practice ({interactiveLessons.length})
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="py-8">
                {mode === 'lessons' && currentLesson ? (
                    <>
                        {/* Lesson Progress */}
                        <div className="max-w-4xl mx-auto px-6 mb-6">
                            <div className="flex items-center justify-between text-sm text-zinc-500 mb-2">
                                <span>Lesson {currentLessonIndex + 1} of {lessons.length}</span>
                                <span>{Math.round(((currentLessonIndex + 1) / lessons.length) * 100)}% Complete</span>
                            </div>
                            <div className="w-full bg-zinc-800 rounded-full h-2">
                                <div
                                    className="bg-amber-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${((currentLessonIndex + 1) / lessons.length) * 100}%` }}
                                />
                            </div>
                        </div>

                        <LessonViewer
                            lesson={currentLesson}
                            isCompleted={progress.completedLessons.includes(currentLesson.id)}
                            onComplete={handleLessonComplete}
                            onNavigate={handleLessonNavigate}
                        />
                    </>
                ) : mode === 'exercises' && currentExercise ? (
                    <>
                        {/* Exercise Progress */}
                        <div className="max-w-3xl mx-auto px-6 mb-6">
                            <div className="flex items-center justify-between text-sm text-zinc-500 mb-2">
                                <span>Exercise {currentExerciseIndex + 1} of {exercises.length}</span>
                                <span>{Math.round(((currentExerciseIndex + 1) / exercises.length) * 100)}% Complete</span>
                            </div>
                            <div className="w-full bg-zinc-800 rounded-full h-2">
                                <div
                                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${((currentExerciseIndex + 1) / exercises.length) * 100}%` }}
                                />
                            </div>
                        </div>

                        <ExercisePlayer
                            exercise={currentExercise}
                            onComplete={handleExerciseComplete}
                        />

                        {/* Exercise Navigation */}
                        <div className="max-w-3xl mx-auto px-6 mt-6">
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setCurrentExerciseIndex(prev => Math.max(0, prev - 1))}
                                    disabled={currentExerciseIndex === 0}
                                    className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                                >
                                    Previous
                                </button>
                                <button
                                    onClick={() => setCurrentExerciseIndex(prev => Math.min(exercises.length - 1, prev + 1))}
                                    disabled={currentExerciseIndex === exercises.length - 1}
                                    className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </>
                ) : mode === 'practice' && interactiveLessons.length > 0 ? (
                    <div className="max-w-4xl mx-auto px-6">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl font-bold mb-2">🎮 Interactive Practice</h2>
                            <p className="text-zinc-400">Learn by playing! The computer will guide you through each concept.</p>
                        </div>

                        <div className="grid gap-4">
                            {interactiveLessons.map((lesson, index) => (
                                <div
                                    key={lesson.id}
                                    className="bg-zinc-900 border border-zinc-700 rounded-xl p-5 hover:border-green-500 transition cursor-pointer"
                                    onClick={() => startInteractive(index)}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-lg bg-green-600 flex items-center justify-center text-xl">
                                                {lesson.mode === 'guided' && '📖'}
                                                {lesson.mode === 'practice' && '🎯'}
                                                {lesson.mode === 'puzzle' && '🧩'}
                                                {lesson.mode === 'freeplay' && '🎮'}
                                            </div>
                                            <div>
                                                <h3 className="font-bold text-lg">{lesson.title}</h3>
                                                <p className="text-zinc-400 text-sm">{lesson.description}</p>
                                                <div className="flex items-center gap-3 mt-2 text-xs text-zinc-500">
                                                    <span className="px-2 py-1 bg-zinc-800 rounded">
                                                        {lesson.mode === 'guided' && '📖 Guided'}
                                                        {lesson.mode === 'practice' && '🎯 Practice'}
                                                        {lesson.mode === 'puzzle' && '🧩 Puzzle'}
                                                        {lesson.mode === 'freeplay' && '🎮 Free Play'}
                                                    </span>
                                                    <span>{lesson.steps.length} steps</span>
                                                    {lesson.estimatedMinutes && (
                                                        <span>~{lesson.estimatedMinutes} min</span>
                                                    )}
                                                    {lesson.difficulty && (
                                                        <span>{'⭐'.repeat(lesson.difficulty)}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <button className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-medium transition">
                                            Start
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <p className="text-zinc-500">No content available</p>
                    </div>
                )}
            </div>
        </div>
    );
}

