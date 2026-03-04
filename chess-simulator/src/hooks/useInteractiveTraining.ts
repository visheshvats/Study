import { useState, useCallback, useRef, useEffect } from 'react';
import { Chess } from 'chess.js';
import type {
    InteractiveLesson,
    InteractiveState,
    InteractiveResult
} from '@/types/interactive';

const INITIAL_STATE: InteractiveState = {
    lesson: null,
    currentStep: 0,
    currentFen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    status: 'not_started',
    mistakes: 0,
    hintsUsed: 0,
    currentHint: null,
    feedback: null,
    feedbackType: null,
    isPlayerTurn: true,
    isComputerThinking: false,
    moveHistory: [],
};

export function useInteractiveTraining() {
    const [state, setState] = useState<InteractiveState>(INITIAL_STATE);
    const gameRef = useRef(new Chess());
    const startTimeRef = useRef<number>(0);
    const computerTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (computerTimeoutRef.current) {
                clearTimeout(computerTimeoutRef.current);
            }
        };
    }, []);

    /** Start a new interactive lesson */
    const startLesson = useCallback((lesson: InteractiveLesson) => {
        // Reset game to initial position
        gameRef.current = new Chess(lesson.initialFen);
        startTimeRef.current = Date.now();

        const isPlayerTurn =
            (lesson.playerColor === 'white' && gameRef.current.turn() === 'w') ||
            (lesson.playerColor === 'black' && gameRef.current.turn() === 'b');

        setState({
            lesson,
            currentStep: 0,
            currentFen: lesson.initialFen,
            status: 'in_progress',
            mistakes: 0,
            hintsUsed: 0,
            currentHint: null,
            feedback: null,
            feedbackType: null,
            isPlayerTurn,
            isComputerThinking: false,
            moveHistory: [],
        });

        // If first step is autoPlay (computer moves first), trigger it
        if (lesson.steps[0]?.autoPlay) {
            playComputerMove(lesson.steps[0].computerMove!, 0, lesson);
        }
    }, []);

    /** Play computer's move with delay */
    const playComputerMove = useCallback((move: string, stepIndex: number, lesson: InteractiveLesson) => {
        setState(prev => ({ ...prev, isComputerThinking: true, isPlayerTurn: false }));

        const delay = lesson.steps[stepIndex]?.autoPlayDelay || 800;

        computerTimeoutRef.current = setTimeout(() => {
            try {
                const result = gameRef.current.move(move);
                if (result) {
                    const newFen = gameRef.current.fen();
                    // stepIndex is already the correct next step (passed as currentStep + 1)
                    const isComplete = stepIndex >= lesson.steps.length;

                    setState(prev => ({
                        ...prev,
                        currentFen: newFen,
                        currentStep: isComplete ? prev.currentStep : stepIndex,
                        status: isComplete ? 'completed' : 'in_progress',
                        isComputerThinking: false,
                        isPlayerTurn: !isComplete,
                        moveHistory: [...prev.moveHistory, move],
                        feedback: isComplete ? lesson.successMessage : null,
                        feedbackType: isComplete ? 'correct' : null,
                    }));
                }
            } catch (e) {
                console.error('Computer move failed:', e);
                setState(prev => ({ ...prev, isComputerThinking: false }));
            }
        }, delay);
    }, []);

    /** Handle user's move attempt */
    const makeMove = useCallback((from: string, to: string, promotion?: string) => {
        if (!state.lesson || state.status !== 'in_progress' || !state.isPlayerTurn) {
            return false;
        }

        const step = state.lesson.steps[state.currentStep];
        if (!step) return false;

        // Try to make the move
        try {
            const moveResult = gameRef.current.move({ from, to, promotion: promotion || 'q' });
            if (!moveResult) return false;

            const moveSan = moveResult.san;
            const expectedMoves = step.expectedMoves || (step.expectedMove ? [step.expectedMove] : []);

            // Check if move is correct
            const isCorrect = expectedMoves.some(expected => {
                // Normalize both moves for comparison
                const normalizedExpected = expected.replace(/[+#]/g, '');
                const normalizedActual = moveSan.replace(/[+#]/g, '');
                return normalizedExpected === normalizedActual;
            });

            if (isCorrect) {
                // Correct move!
                const newFen = gameRef.current.fen();
                const hasComputerResponse = !!step.computerMove;
                const nextStep = hasComputerResponse ? state.currentStep : state.currentStep + 1;
                const isComplete = !hasComputerResponse && nextStep >= state.lesson.steps.length;

                setState(prev => ({
                    ...prev,
                    currentFen: newFen,
                    currentStep: nextStep,
                    feedback: step.feedback.correct,
                    feedbackType: 'correct',
                    currentHint: null,
                    isPlayerTurn: !hasComputerResponse && !isComplete,
                    status: isComplete ? 'completed' : 'in_progress',
                    moveHistory: [...prev.moveHistory, moveSan],
                }));

                // If there's a computer response, play it
                if (hasComputerResponse) {
                    playComputerMove(step.computerMove!, state.currentStep + 1, state.lesson);
                }

                return true;
            } else {
                // Wrong move - undo it
                gameRef.current.undo();
                setState(prev => ({
                    ...prev,
                    mistakes: prev.mistakes + 1,
                    feedback: step.feedback.incorrect,
                    feedbackType: 'incorrect',
                }));
                return false;
            }
        } catch (e) {
            console.error('Move error:', e);
            return false;
        }
    }, [state, playComputerMove]);

    /** Request a hint */
    const requestHint = useCallback(() => {
        if (!state.lesson) return;

        const step = state.lesson.steps[state.currentStep];
        const hints = state.lesson.hints || [];

        // Show hint based on how many have been used
        let hint: string;
        if (state.hintsUsed < hints.length) {
            hint = hints[state.hintsUsed];
        } else if (step.expectedMove || step.expectedMoves) {
            // Last resort: show the move
            const move = step.expectedMove || step.expectedMoves![0];
            hint = `Try moving: ${move}`;
        } else {
            hint = 'No hints available for this step.';
        }

        setState(prev => ({
            ...prev,
            hintsUsed: prev.hintsUsed + 1,
            currentHint: hint,
        }));
    }, [state]);

    /** Reset to initial position of current lesson */
    const resetLesson = useCallback(() => {
        if (state.lesson) {
            startLesson(state.lesson);
        }
    }, [state.lesson, startLesson]);

    /** Get session result */
    const getResult = useCallback((): InteractiveResult | null => {
        if (!state.lesson) return null;

        return {
            lessonId: state.lesson.id,
            completed: state.status === 'completed',
            mistakes: state.mistakes,
            hintsUsed: state.hintsUsed,
            timeSpent: Math.round((Date.now() - startTimeRef.current) / 1000),
            timestamp: new Date(),
        };
    }, [state]);

    /** Clear current session */
    const clearSession = useCallback(() => {
        if (computerTimeoutRef.current) {
            clearTimeout(computerTimeoutRef.current);
        }
        setState(INITIAL_STATE);
    }, []);

    /** Get current step info */
    const getCurrentStep = useCallback(() => {
        if (!state.lesson || state.currentStep >= state.lesson.steps.length) {
            return null;
        }
        return state.lesson.steps[state.currentStep];
    }, [state]);

    return {
        state,
        startLesson,
        makeMove,
        requestHint,
        resetLesson,
        getResult,
        clearSession,
        getCurrentStep,
    };
}
