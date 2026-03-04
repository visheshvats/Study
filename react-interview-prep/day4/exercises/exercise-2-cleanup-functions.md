# Exercise 2: Cleanup Functions (15 mins)

## 🎯 Goal
Practice cleanup functions with timers and prevent memory leaks.

## 📝 Instructions

Create a `Timer.jsx` component that:
- Shows a timer that counts up every second
- Has Start/Stop buttons
- Properly cleans up the interval
- Shows a countdown timer (separate feature)

**Starter code:**
```jsx
import { useState, useEffect } from 'react';

function Timer() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [countdown, setCountdown] = useState(10);

  // TODO: Effect for counting up timer
  // Should run when isRunning changes
  // MUST clean up the interval!
  useEffect(() => {
    if (isRunning) {
      // Start interval
      const intervalId = setInterval(() => {
        // Increment seconds
      }, 1000);
      
      // TODO: Return cleanup function
      return () => {
        // Clear the interval
      };
    }
  }, [/* dependencies? */]);

  // TODO: Effect for countdown timer
  // Runs once on mount, counts down from 10 to 0
  // Stops at 0 and cleans up
  useEffect(() => {
    const intervalId = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          // TODO: Stop interval when reaching 0
          clearInterval(intervalId);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // TODO: Cleanup function
    return () => {
      // Clear interval on unmount
    };
  }, []); // Run once on mount

  return (
    <div style={{ padding: '20px' }}>
      <h2>Timer Demo</h2>
      
      {/* Counting Up Timer */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '2px solid #4CAF50', borderRadius: '8px' }}>
        <h3>Stopwatch</h3>
        <div style={{ fontSize: '48px', fontWeight: 'bold', textAlign: 'center', margin: '20px 0' }}>
          {seconds}s
        </div>
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <button 
            onClick={() => setIsRunning(true)}
            disabled={isRunning}
            style={{ padding: '10px 20px' }}
          >
            Start
          </button>
          <button 
            onClick={() => setIsRunning(false)}
            disabled={!isRunning}
            style={{ padding: '10px 20px' }}
          >
            Stop
          </button>
          <button 
            onClick={() => {
              setSeconds(0);
              setIsRunning(false);
            }}
            style={{ padding: '10px 20px' }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Countdown Timer */}
      <div style={{ padding: '20px', border: '2px solid #FF9800', borderRadius: '8px' }}>
        <h3>Countdown (auto-started)</h3>
        <div style={{ 
          fontSize: '48px', 
          fontWeight: 'bold', 
          textAlign: 'center',
          color: countdown === 0 ? 'red' : 'black',
          margin: '20px 0' 
        }}>
          {countdown}s
        </div>
        {countdown === 0 && (
          <p style={{ textAlign: 'center', color: 'red', fontWeight: 'bold' }}>
            Time's up! 🎉
          </p>
        )}
      </div>
    </div>
  );
}

export default Timer;
```

## ✅ Acceptance Criteria
- [ ] Stopwatch starts when clicking Start
- [ ] Stopwatch stops when clicking Stop
- [ ] Reset button works correctly
- [ ] Countdown starts automatically at 10
- [ ] Countdown stops at 0
- [ ] Both timers clean up their intervals
- [ ] No intervals running after component unmounts
- [ ] No console warnings

## 🐛 Edge Cases
- What happens if you click Start multiple times? (Should be disabled)
- What if component unmounts while timer is running? (Should clean up)
- Test by starting timer, then hiding component

## 📋 Self-Review Checklist
- [ ] Used `setInterval` correctly
- [ ] Returned cleanup function with `clearInterval`
- [ ] Stopwatch uses `[isRunning]` as dependency
- [ ] Countdown uses `[]` as dependency
- [ ] No memory leaks (cleanup on unmount)
- [ ] Timers can be stopped properly

## 💡 Complete Solution

```jsx
// Stopwatch effect
useEffect(() => {
  if (isRunning) {
    const intervalId = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
    
    return () => {
      clearInterval(intervalId);
    };
  }
}, [isRunning]);

// Countdown effect
useEffect(() => {
  const intervalId = setInterval(() => {
    setCountdown(prev => {
      if (prev <= 1) {
        clearInterval(intervalId);
        return 0;
      }
      return prev - 1;
    });
  }, 1000);

  return () => {
    clearInterval(intervalId);
  };
}, []);
```

## 💡 Bonus Challenges

1. **Add a pause feature** for the countdown
2. **Add sound** when countdown reaches 0 (use Audio API)
3. **Add custom duration** input for countdown
4. **Show milliseconds** in the stopwatch

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to Exercise 3!
