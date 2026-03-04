# Exercise 2: useRef for Stable Values (15 mins)

## 🎯 Goal
Use useRef to store mutable values that don't trigger re-renders.

## 📝 Instructions

Create a `RenderCounter.jsx` component that:
- Counts how many times the component rendered
- Tracks the previous value of a state variable
- Stores an interval ID without causing re-renders

**Starter code:**
```jsx
import { useState, useEffect, useRef } from 'react';

function RenderCounter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  // TODO: Create ref to track render count
  const renderCount = useRef(0);
  
  // TODO: Create ref to track previous value
  const prevCountRef = useRef();
  
  // TODO: Create ref to store interval ID
  const intervalRef = useRef(null);

  // Track renders
  useEffect(() => {
    // TODO: Increment renderCount.current
    // This doesn't cause re-render!
  });

  // Track previous count
  useEffect(() => {
    // TODO: Store current count as previous for next render
  }, [count]);

  const startAutoIncrement = () => {
    // TODO: Start interval that increments count every second
    // Store interval ID in intervalRef.current
  };

  const stopAutoIncrement = () => {
    // TODO: Clear the interval using intervalRef.current
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>useRef for Stable Values Demo</h2>
      
      {/* Render Counter */}
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h3>Render Count: {renderCount.current}</h3>
        <p style={{ fontSize: '14px', color: '#666' }}>
          This counts renders without causing re-renders itself!
        </p>
      </div>

      {/* Previous Value Tracker */}
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
        <h3>Count: {count}</h3>
        <p>Previous count: {prevCountRef.current ?? 'N/A'}</p>
        <button onClick={() => setCount(count + 1)}>Increment</button>
      </div>

      {/* Auto Increment */}
      <div style={{ padding: '15px', backgroundColor: '#fff3e0', borderRadius: '4px' }}>
        <h3>Auto Increment</h3>
        <p>Count will increment automatically every second</p>
        <button onClick={startAutoIncrement} style={{ marginRight: '10px' }}>
          Start
        </button>
        <button onClick={stopAutoIncrement}>
          Stop
        </button>
      </div>

      {/* Name Input (to trigger additional renders) */}
      <div style={{ marginTop: '20px' }}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Type to trigger renders..."
          style={{ padding: '8px' }}
        />
        <p style={{ fontSize: '12px', color: '#666' }}>
          Notice render count increases as you type!
        </p>
      </div>
    </div>
  );
}

export default RenderCounter;
```

## ✅ Acceptance Criteria
- [ ] Render count updates on every render
- [ ] Render count doesn't cause additional renders
- [ ] Previous count displays correctly
- [ ] Auto-increment starts and stops properly
- [ ] Interval is cleaned up properly
- [ ] Render count increases when typing in input

## 🐛 Edge Cases
- What if you click Start multiple times? (Should clear previous interval)
- What if component unmounts while interval is running? (Should cleanup)

## 📋 Self-Review Checklist
- [ ] Used `useRef()` not `useState()` for values that don't affect UI
- [ ] Accessed ref values with `.current`
- [ ] Modified ref values directly (no setter function)
- [ ] Cleaned up interval on unmount

## 💡 Complete Solution

```jsx
import { useState, useEffect, useRef } from 'react';

function RenderCounter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  const renderCount = useRef(0);
  const prevCountRef = useRef();
  const intervalRef = useRef(null);

  // Track renders (runs after every render)
  useEffect(() => {
    renderCount.current += 1;
  });

  // Track previous count
  useEffect(() => {
    prevCountRef.current = count;
  }, [count]);

  const startAutoIncrement = () => {
    // Clear existing interval if any
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Start new interval
    intervalRef.current = setInterval(() => {
      setCount(prev => prev + 1);
    }, 1000);
  };

  const stopAutoIncrement = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // ... rest of component
}
```

## 💡 Key Insights

**Why useRef instead of useState for render count?**
```jsx
// ❌ BAD - Infinite loop!
const [renderCount, setRenderCount] = useState(0);
useEffect(() => {
  setRenderCount(renderCount + 1); // Causes re-render!
  // → which runs effect again → infinite loop
});

// ✅ GOOD - No re-render
const renderCount = useRef(0);
useEffect(() => {
  renderCount.current += 1; // No re-render!
});
```

**Why useRef for interval ID?**
- Interval ID needs to persist across renders
- Don't want to trigger re-render when storing ID
- Need to access it in cleanup and stop handler

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to Exercise 3!
