# Exercise 1: useEffect Basics (10 mins)

## 🎯 Goal
Practice using useEffect with different dependency arrays.

## 📝 Instructions

Create a `EffectDemo.jsx` component that demonstrates three different useEffect patterns:

1. **Document title updater** - Updates page title with a counter
2. **Mount logger** - Logs to console only on mount
3. **Conditional logger** - Logs when a specific value changes

**Starter code:**
```jsx
import { useState, useEffect } from 'react';

function EffectDemo() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  // TODO: Effect 1 - Update document title with count
  // Should run every time count changes
  useEffect(() => {
    // Update document.title here
  }, [/* dependencies? */]);

  // TODO: Effect 2 - Log "Component mounted!" once
  // Should run only on mount
  useEffect(() => {
    // Log here
  }, [/* dependencies? */]);

  // TODO: Effect 3 - Log "Name changed to: {name}" when name changes
  // Should run only when name changes (not on mount)
  useEffect(() => {
    if (name) { // Only log if name is not empty
      // Log here
    }
  }, [/* dependencies? */]);

  return (
    <div style={{ padding: '20px' }}>
      <h2>useEffect Demo</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Counter: {count}</h3>
        <button onClick={() => setCount(count + 1)}>Increment</button>
        <p style={{ fontSize: '12px', color: '#666' }}>
          Check the page title - it should show the count!
        </p>
      </div>

      <div>
        <h3>Name Input</h3>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name..."
          style={{ padding: '8px' }}
        />
        <p style={{ fontSize: '12px', color: '#666' }}>
          Check the console when you type!
        </p>
      </div>

      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h4>What to check:</h4>
        <ul style={{ fontSize: '14px' }}>
          <li>Page title updates when you click increment</li>
          <li>Console shows "Component mounted!" once when page loads</li>
          <li>Console logs name changes as you type</li>
        </ul>
      </div>
    </div>
  );
}

export default EffectDemo;
```

## ✅ Acceptance Criteria
- [ ] Document title updates when count changes
- [ ] "Component mounted!" logs once on initial render
- [ ] Name changes log to console as you type
- [ ] Each effect has correct dependency array
- [ ] No infinite loops
- [ ] No unnecessary re-runs

## 🐛 Edge Cases
- What if you increment count rapidly?
- What if you clear the name field?

## 📋 Self-Review Checklist
- [ ] Imported useEffect from 'react'
- [ ] Effect 1 has `[count]` as dependency
- [ ] Effect 2 has `[]` as dependency (empty array)
- [ ] Effect 3 has `[name]` as dependency
- [ ] Document title actually updates
- [ ] Console logs appear correctly

## 💡 Solution

```jsx
// Effect 1: Update title when count changes
useEffect(() => {
  document.title = `Count: ${count}`;
}, [count]);

// Effect 2: Log once on mount
useEffect(() => {
  console.log('Component mounted!');
}, []);

// Effect 3: Log when name changes
useEffect(() => {
  if (name) {
    console.log(`Name changed to: ${name}`);
  }
}, [name]);
```

---

**Time limit:** 10 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 2!
