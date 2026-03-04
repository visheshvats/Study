# Exercise 3: useMemo and useCallback (20 mins)

## 🎯 Goal
Practice using useMemo and useCallback (and understand when NOT to use them).

## 📝 Instructions

Create a `OptimizationDemo.jsx` component that demonstrates:
- Expensive calculation with useMemo
- Memoized callback with useCallback
- Comparison: with and without optimization

**Starter code:**
```jsx
import { useState, useMemo, useCallback } from 'react';

// Simple memoized child component
const ChildComponent = React.memo(({ onClick, data }) => {
  console.log('ChildComponent rendered');
  return (
    <div style={{ padding: '10px', border: '1px solid #ddd', marginTop: '10px' }}>
      <p>Child Component (React.memo)</p>
      <p>Data: {data}</p>
      <button onClick={onClick}>Click from Child</button>
    </div>
  );
});

function OptimizationDemo() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([1, 2, 3, 4, 5]);
  const [filter, setFilter] = useState('');

  console.log('Parent rendered');

  // TODO: Expensive calculation WITHOUT useMemo
  // This runs on EVERY render (even when 'items' didn't change)
  const expensiveCalculationWithout = () => {
    console.log('Running expensive calculation (NO useMemo)...');
    let sum = 0;
    for (let i = 0; i < items.length; i++) {
      // Simulate expensive work
      for (let j = 0; j < 1000000; j++) {
        sum += items[i];
      }
    }
    return sum;
  };
  const totalWithout = expensiveCalculationWithout();

  // TODO: Expensive calculation WITH useMemo
  // This only runs when 'items' changes
  const totalWith = useMemo(() => {
    console.log('Running expensive calculation (WITH useMemo)...');
    let sum = 0;
    for (let i = 0; i < items.length; i++) {
      for (let j = 0; j < 1000000; j++) {
        sum += items[i];
      }
    }
    return sum;
  }, [/* dependencies? */]);

  // TODO: Callback WITHOUT useCallback
  // New function on every render
  const handleClickWithout = () => {
    console.log('Clicked without useCallback');
    setCount(count + 1);
  };

  // TODO: Callback WITH useCallback
  // Same function reference unless dependencies change
  const handleClickWith = useCallback(() => {
    console.log('Clicked with useCallback');
    setCount(prev => prev + 1);
  }, [/* dependencies? */]);

  return (
    <div style={{ padding: '20px' }}>
      <h2>useMemo & useCallback Demo</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Count: {count}</h3>
        <button onClick={() => setCount(count + 1)}>Increment Count</button>
        <p style={{ fontSize: '12px', color: '#666' }}>
          Click and watch console - which calculations re-run?
        </p>
      </div>

      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h4>Expensive Calculation Results:</h4>
        <p>Without useMemo: {totalWithout}</p>
        <p>With useMemo: {totalWith}</p>
        <p style={{ fontSize: '12px', color: '#666' }}>
          Check console: without useMemo runs every render, with useMemo only when items change
        </p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setItems([...items, items.length + 1])}>
          Add Item (triggers useMemo)
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4>Filter (doesn't affect calculation):</h4>
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Type to trigger render..."
          style={{ padding: '8px' }}
        />
      </div>

      <div>
        <h4>Child Components:</h4>
        <ChildComponent onClick={handleClickWithout} data="Without useCallback" />
        <ChildComponent onClick={handleClickWith} data="With useCallback" />
        <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
          Watch console: WITHOUT useCallback, child re-renders every time parent renders.
          WITH useCallback, child only re-renders when callback dependencies change.
        </p>
      </div>
    </div>
  );
}

export default OptimizationDemo;
```

## ✅ Acceptance Criteria
- [ ] useMemo only recalculates when items change
- [ ] Without useMemo runs on every render
- [ ] useCallback prevents child re-renders
- [ ] Console logs show the difference
- [ ] Dependencies are correct

## 🐛 Edge Cases
- What if you forget dependencies? (Stale values!)
- What if you add all dependencies? (Less benefit from memoization)

## 📋 Self-Review Checklist
- [ ] Imported React for React.memo
- [ ] useMemo has `[items]` as dependency
- [ ] useCallback has `[]` or uses prev => pattern
- [ ] Console shows optimization working
- [ ] Child component wrapped in React.memo

## 💡 Complete Solution

```jsx
import React, { useState, useMemo, useCallback } from 'react';

const ChildComponent = React.memo(({ onClick, data }) => {
  console.log(`ChildComponent rendered: ${data}`);
  return (
    <div style={{ padding: '10px', border: '1px solid #ddd', marginTop: '10px' }}>
      <p>Child Component (React.memo)</p>
      <p>Data: {data}</p>
      <button onClick={onClick}>Click from Child</button>
    </div>
  );
});

function OptimizationDemo() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([1, 2, 3, 4, 5]);
  const [filter, setFilter] = useState('');

  console.log('Parent rendered');

  // Without useMemo (runs every render)
  const expensiveCalculationWithout = () => {
    console.log('Running expensive calculation (NO useMemo)...');
    let sum = 0;
    for (let i = 0; i < items.length; i++) {
      for (let j = 0; j < 1000000; j++) {
        sum += items[i];
      }
    }
    return sum;
  };
  const totalWithout = expensiveCalculationWithout();

  // With useMemo (only runs when items changes)
  const totalWith = useMemo(() => {
    console.log('Running expensive calculation (WITH useMemo)...');
    let sum = 0;
    for (let i = 0; i < items.length; i++) {
      for (let j = 0; j < 1000000; j++) {
        sum += items[i];
      }
    }
    return sum;
  }, [items]);

  // Without useCallback (new function every render)
  const handleClickWithout = () => {
    console.log('Clicked without useCallback');
    setCount(count + 1);
  };

  // With useCallback (stable function reference)
  const handleClickWith = useCallback(() => {
    console.log('Clicked with useCallback');
    setCount(prev => prev + 1); // Use functional update to avoid count dependency
  }, []); // Empty array = never changes

  // ... rest of component
}
```

## 💡 Key Insights

**When useMemo helps:**
- Expensive calculation runs on every render (even when inputs unchanged)
- With useMemo: only recalculates when dependencies change
- See console: "NO useMemo" logs on every render, "WITH useMemo" only when items changes

**When useCallback helps:**
- Child wrapped in React.memo
- Without useCallback: new function → child thinks props changed → re-renders
- With useCallback: same function → React.memo prevents re-render

**Important Notes:**
```jsx
// ❌ BAD - Has dependency on count
const handleClick = useCallback(() => {
  setCount(count + 1);
}, [count]); // New function when count changes → defeats purpose!

// ✅ GOOD - No dependencies needed
const handleClick = useCallback(() => {
  setCount(prev => prev + 1); // Functional update
}, []); // Never changes → stable reference
```

---

**Time limit:** 20 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to the Interview Question!
