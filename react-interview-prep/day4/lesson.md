# Day 4: useEffect Deep Dive I

## 📖 3-Minute Concept Lesson

### 1. useEffect Basics

**What it is:**  
`useEffect` lets you perform **side effects** in function components. Side effects are anything that reaches outside your component: data fetching, subscriptions, timers, manual DOM changes, etc.

```jsx
import { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    // This runs after every render
    document.title = `Count: ${count}`;
  });
  
  return <button onClick={() => setCount(count + 1)}>Click</button>;
}
```

**When to use:**
- Fetching data from an API
- Setting up subscriptions or timers
- Manually changing the DOM
- Logging or analytics
- Reading from localStorage

**Common mistakes:**
- ❌ Using it for calculations (use regular variables instead)
- ❌ Updating state without proper dependencies (infinite loops!)
- ❌ Forgetting the dependency array (runs on every render)
- ❌ Not cleaning up side effects (memory leaks!)

**Tiny example:**
```jsx
// ❌ Bad - runs on EVERY render
useEffect(() => {
  console.log('Rendered!');
});

// ✅ Good - runs only once on mount
useEffect(() => {
  console.log('Component mounted!');
}, []); // ← Empty array = run once
```

---

### 2. Dependency Arrays

**What it is:**  
The second argument to `useEffect` controls when the effect runs. It's an array of values the effect depends on.

```jsx
useEffect(() => {
  // Effect code
}, [dependency1, dependency2]); // ← Runs when these change
```

**Three patterns:**

**Pattern 1: No dependency array** (runs after every render)
```jsx
useEffect(() => {
  console.log('Every render');
});
```

**Pattern 2: Empty array `[]`** (runs once on mount)
```jsx
useEffect(() => {
  console.log('Only on mount');
}, []);
```

**Pattern 3: With dependencies** (runs when dependencies change)
```jsx
useEffect(() => {
  console.log('When count or name changes');
}, [count, name]);
```

**When to use:**
- **No array:** Rarely! Only when you need to run on every render
- **Empty `[]`:** Initial data fetching, setup subscriptions, one-time setup
- **With deps:** Re-fetch data when search query changes, update based on props/state

**Common mistakes:**
- ❌ Missing dependencies ESLint warns about
- ❌ Using objects/arrays as dependencies (always "different")
- ❌ Not listing all used values from props/state
- ❌ Infinite loops: `useEffect(() => setCount(count + 1))` with no deps

**Tiny example:**
```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    // Fetch user when userId changes
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data));
  }, [userId]); // ← Re-run when userId changes
  
  return <div>{user?.name}</div>;
}
```

---

### 3. Cleanup Functions

**What it is:**  
Return a function from `useEffect` to clean up side effects. This runs before the component unmounts or before the effect runs again.

```jsx
useEffect(() => {
  // Setup
  const timer = setInterval(() => {
    console.log('Tick');
  }, 1000);
  
  // Cleanup
  return () => {
    clearInterval(timer);
  };
}, []);
```

**When to use:**
- Clear timers/intervals
- Cancel network requests
- Unsubscribe from subscriptions
- Remove event listeners
- Clean up WebSocket connections

**Common mistakes:**
- ❌ Forgetting to cleanup timers (keeps running after unmount!)
- ❌ Not unsubscribing from events (memory leaks!)
- ❌ Not canceling fetch requests (state updates on unmounted component)

**Tiny example:**
```jsx
function Clock() {
  const [time, setTime] = useState(new Date());
  
  useEffect(() => {
    // Setup: Start interval
    const intervalId = setInterval(() => {
      setTime(new Date());
    }, 1000);
    
    // Cleanup: Clear interval when component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, []); // Empty array = setup once, cleanup on unmount
  
  return <div>{time.toLocaleTimeString()}</div>;
}
```

**Without cleanup:**
```jsx
// ❌ BAD - interval keeps running even after component removed!
useEffect(() => {
  setInterval(() => setTime(new Date()), 1000);
}, []);
```

---

## 🔑 Key Takeaways

1. **useEffect** = Run side effects after render
2. **Dependencies** = Control when effect runs (none, empty, or specific values)
3. **Cleanup** = Return function to clean up (timers, subscriptions, listeners)

---

## ⚠️ Interview Tips

**Common questions:**

> **"What is useEffect for?"**  
> **Answer:** useEffect lets you perform side effects in function components. Side effects include data fetching, subscriptions, timers, or manually changing the DOM. It runs after render and can optionally clean up before the next effect or unmount.

> **"What's the dependency array in useEffect?"**  
> **Answer:** The second argument to useEffect controls when it runs. An empty array means run once on mount. An array with values means run when those values change. No array means run after every render. React compares dependencies using Object.is equality.

> **"Why do we need cleanup functions?"**  
> **Answer:** Cleanup prevents memory leaks and bugs. Without cleanup, timers keep running, event listeners accumulate, and subscriptions stay active even after the component unmounts. The cleanup function runs before re-running the effect and when the component unmounts.

> **"What happens if you update state in useEffect without dependencies?"**  
> **Answer:** Infinite loop! The effect runs after render, updates state, triggers re-render, effect runs again, infinite cycle. Always include proper dependencies or use empty array if it should run once.

---

## ✅ Self-Check Questions

Before moving to exercises:

1. When does useEffect run (with different dependency arrays)?
2. What's the difference between `[]`, `[count]`, and no array?
3. When do I need a cleanup function?
4. How do I avoid infinite loops with useEffect?

If yes to all, proceed to exercises! 🎉

---

**Next:** `exercises/` folder for hands-on practice!
