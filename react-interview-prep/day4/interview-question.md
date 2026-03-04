# Day 4 Interview Question

## ❓ Question

**Interviewer asks:**

> "I want you to build a component that fetches and displays a list of posts from an API. The component should show a loading spinner while fetching, handle errors gracefully, and allow the user to refresh the data. Can you implement this with proper useEffect usage?"

**API to use:** `https://jsonplaceholder.typicode.com/posts`

**Additional requirements:**
- Show loading state
- Show error state with retry button
- Display all posts (title and body)
- Add a refresh button
- Handle component unmounting during fetch

**Then explain:**
1. Why you chose those specific dependencies
2. What would happen without cleanup
3. How you handle the race condition

---

## 📝 Your Task

Write the complete component with:
1. **State management** (posts, loading, error)
2. **useEffect** with proper dependencies
3. **Fetch logic** with error handling
4. **Cleanup** (abort controller to cancel requests)
5. **Conditional rendering** for loading/error/success
6. **Refresh functionality**

Also explain:
- Why dependencies matter
- When cleanup is needed
- How to prevent race conditions

---

## ✅ Evaluation Criteria

Your code should include:
- [ ] Three states: loading, error, posts
- [ ] useEffect for data fetching
- [ ] Proper dependency array
- [ ] Error handling with try/catch or .catch()
- [ ] AbortController for cleanup
- [ ] Conditional rendering for all states
- [ ] Refresh button that works correctly

Your explanation should cover:
- [ ] Why empty dependency array for initial fetch
- [ ] Why cleanup prevents memory leaks
- [ ] How race conditions happen and how to prevent them

---

## 🎯 Model Answer (Don't peek until you've tried!)

<details>
<summary>Click to reveal answer</summary>

### Code Solution:

```jsx
import { useState, useEffect } from 'react';

function PostList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    // Create AbortController for cleanup
    const controller = new AbortController();
    
    // Reset states
    setLoading(true);
    setError(null);

    // Fetch data
    fetch('https://jsonplaceholder.typicode.com/posts', {
      signal: controller.signal // Pass abort signal
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setPosts(data);
        setLoading(false);
      })
      .catch(err => {
        // Ignore abort errors (happens when component unmounts)
        if (err.name === 'AbortError') {
          console.log('Fetch aborted');
          return;
        }
        setError(err.message);
        setLoading(false);
      });

    // Cleanup function
    return () => {
      controller.abort(); // Cancel the request if component unmounts
    };
  }, [refreshKey]); // Re-run when refreshKey changes
  
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1); // Trigger re-fetch
  };

  // Loading state
  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2>Loading posts...</h2>
        <div style={{ fontSize: '64px' }}>⏳</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ color: 'red' }}>Error Loading Posts</h2>
        <p>{error}</p>
        <button 
          onClick={handleRefresh}
          style={{
            padding: '10px 20px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  // Success state
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Posts ({posts.length})</h1>
        <button 
          onClick={handleRefresh}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔄 Refresh
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {posts.slice(0, 10).map(post => ( // Show first 10 for brevity
          <div 
            key={post.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              backgroundColor: '#f9f9f9'
            }}
          >
            <h3 style={{ marginTop: 0, color: '#333' }}>
              {post.id}. {post.title}
            </h3>
            <p style={{ color: '#666', marginBottom: 0 }}>
              {post.body}
            </p>
          </div>
        ))}
      </div>

      {posts.length > 10 && (
        <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
          Showing 10 of {posts.length} posts
        </p>
      )}
    </div>
  );
}

export default PostList;
```

---

### Explanation:

#### 1. Why These Dependencies?

```jsx
useEffect(() => {
  // fetch code
}, [refreshKey]);
```

- **`[refreshKey]`** - Effect runs when refreshKey changes
- Changing refreshKey triggers re-fetch without directly calling fetch
- Could also use `[]` and rely on refresh function to manually re-fetch
- This pattern is cleaner - useState + useEffect working together

#### 2. Why Cleanup is Critical

**Without cleanup:**
```jsx
// ❌ BAD - No cleanup
useEffect(() => {
  fetch(url)
    .then(res => res.json())
    .then(data => setPosts(data)); // ← DANGER!
}, []);
```

**Problem:** If component unmounts before fetch completes:
- Fetch finishes after unmount
- Tries to call `setPosts` on unmounted component
- React warning: "Can't perform state update on unmounted component"
- Memory leak and potential bugs

**With cleanup:**
```jsx
// ✅ GOOD - With cleanup
useEffect(() => {
  const controller = new AbortController();
  
  fetch(url, { signal: controller.signal })
    .then(...)
    .catch(err => {
      if (err.name === 'AbortError') return; // Ignore aborts
      setError(err.message);
    });
  
  return () => controller.abort(); // Cancel on unmount!
}, []);
```

**Benefits:**
- Request cancelled if component unmounts
- No state updates on unmounted components
- No memory leaks
- Clean, predictable behavior

#### 3. Race Conditions Explained

**What's a race condition?**

Imagine user clicks "Next User" rapidly:
1. Click → Fetch user 1 (slow network, takes 3 seconds)
2. Click → Fetch user 2 (fast network, takes 0.5 seconds)
3. User 2 data arrives first → Shows user 2 ✓
4. User 1 data arrives later → Shows user 1 ✗ (WRONG!)

**The problem:** Requests can finish out of order!

**How our solution prevents this:**

```jsx
useEffect(() => {
  const controller = new AbortController();
  
  fetch(url, { signal: controller.signal })
    .then(...)
  
  return () => controller.abort(); // ← Cancels previous request!
}, [refreshKey]);
```

When `refreshKey` changes:
1. Cleanup runs → Aborts old request
2. New effect runs → Starts new request
3. Only latest request can complete
4. Old requests are cancelled → No race condition!

#### 4. State Management Strategy

**Three states for async data:**
```jsx
const [posts, setPosts] = useState([]);       // The data
const [loading, setLoading] = useState(true); // Is it loading?
const [error, setError] = useState(null);     // Did it fail?
```

**State transitions:**
```
Initial: loading=true, error=null, posts=[]
  ↓
Fetching: loading=true, error=null, posts=[]
  ↓
Success: loading=false, error=null, posts=[...]
OR
Error: loading=false, error="message", posts=[]
```

**Why this pattern:**
- Clear separation of concerns
- Easy to add retry logic
- Can show different UI for each state
- Industry standard pattern

#### 5. Interview Tips

**When explaining this in an interview:**

1. **Start with the big picture:** "I'll fetch data on mount, show loading/error states, and handle cleanup"

2. **Explain as you code:** "I'm using AbortController because..." (don't code silently)

3. **Mention edge cases:** "If the component unmounts during fetch, we need to cancel the request"

4. **Show you understand async:** "Fetch returns a promise, so I need loading states while it's pending"

5. **Talk about UX:** "Users should see a spinner so they know something is happening"

6. **Discuss race conditions:** "If requests finish out of order, we could show stale data"

</details>

---

## 💬 When You're Ready

Write your solution and explanation, then paste here for review. I'll evaluate:
- useEffect usage and dependencies
- Cleanup implementation
- Error handling
- State management
- Understanding of async patterns
- Interview communication quality

**Remember:** Being able to explain WHY you made each choice is what separates good interviews from great ones!
