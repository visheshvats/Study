// Interactive Training Type Definitions

import type { Arrow } from './curriculum';

/** Mode of interactive training */
export type InteractiveMode = 'guided' | 'practice' | 'puzzle' | 'freeplay';

/** Status of the interactive session */
export type SessionStatus = 'not_started' | 'in_progress' | 'completed' | 'failed';

/** Individual step in an interactive lesson */
export interface InteractiveStep {
    /** Instruction to show the user */
    instruction: string;
    /** Expected move in SAN notation (e.g., "Nf3") */
    expectedMove?: string;
    /** Multiple accepted moves (any one is correct) */
    expectedMoves?: string[];
    /** Computer's response move after user's correct move */
    computerMove?: string;
    /** Feedback messages */
    feedback: {
        correct: string;
        incorrect: string;
    };
    /** Squares to highlight on the board */
    highlight?: string[];
    /** Arrows to show on the board */
    arrows?: Arrow[];
    /** If true, this is a computer-initiated move (no user input needed) */
    autoPlay?: boolean;
    /** Delay before auto-play move (ms) */
    autoPlayDelay?: number;
}

/** An interactive lesson/training session */
export interface InteractiveLesson {
    /** Unique ID */
    id: string;
    /** Related lesson ID (if any) */
    lessonId?: string;
    /** Module this belongs to */
    moduleId: string;
    /** Display title */
    title: string;
    /** Short description */
    description: string;
    /** Type of interactive training */
    mode: InteractiveMode;
    /** Starting position (FEN) */
    initialFen: string;
    /** Which color the player controls */
    playerColor: 'white' | 'black';
    /** Steps to complete */
    steps: InteractiveStep[];
    /** Message shown on successful completion */
    successMessage: string;
    /** Optional hints user can request */
    hints?: string[];
    /** Estimated time in minutes */
    estimatedMinutes?: number;
    /** Difficulty rating 1-5 */
    difficulty?: 1 | 2 | 3 | 4 | 5;
}

/** Result of an interactive training session */
export interface InteractiveResult {
    lessonId: string;
    completed: boolean;
    mistakes: number;
    hintsUsed: number;
    timeSpent: number; // seconds
    timestamp: Date;
}

/** State for the interactive training hook */
export interface InteractiveState {
    /** Current lesson being practiced */
    lesson: InteractiveLesson | null;
    /** Current step index */
    currentStep: number;
    /** Current board position (FEN) */
    currentFen: string;
    /** Session status */
    status: SessionStatus;
    /** Number of mistakes made */
    mistakes: number;
    /** Number of hints used */
    hintsUsed: number;
    /** Current hint being shown (if any) */
    currentHint: string | null;
    /** Latest feedback message */
    feedback: string | null;
    /** Is feedback positive (correct) or negative (incorrect) */
    feedbackType: 'correct' | 'incorrect' | null;
    /** Is it the player's turn? */
    isPlayerTurn: boolean;
    /** Is the computer "thinking" (playing with delay)? */
    isComputerThinking: boolean;
    /** Move history for this session */
    moveHistory: string[];
}

/** Container for interactive lessons by module */
export interface ModuleInteractiveLessons {
    moduleId: string;
    lessons: InteractiveLesson[];
}
