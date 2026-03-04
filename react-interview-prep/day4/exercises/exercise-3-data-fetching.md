# Exercise 3: Data Fetching with useEffect (20 mins)

## 🎯 Goal
Fetch data from an API using useEffect with proper loading and error states.

## 📝 Instructions

Create a `UserFetcher.jsx` component that:
- Fetches user data from an API on mount
- Shows loading state while fetching
- Shows error state if fetch fails
- Displays user data when successful
- Can refetch data on button click

We'll use JSONPlaceholder API: `https://jsonplaceholder.typicode.com/users/1`

**Starter code:**
```jsx
import { useState, useEffect } from 'react';

function UserFetcher() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userId, setUserId] = useState(1);

  useEffect(() => {
    // Reset states
    setLoading(true);
    setError(null);

    // TODO: Fetch user data
    fetch(`https://jsonplaceholder.typicode.com/users/${userId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch user');
        }
        return response.json();
      })
      .then(data => {
        // TODO: Set user data
        // TODO: Set loading to false
      })
      .catch(err => {
        // TODO: Set error message
        // TODO: Set loading to false
      });

  }, [/* dependencies? */]); // When should this re-run?

  // Loading state
  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Loading...</h2>
        <div style={{ fontSize: '48px' }}>⏳</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2 style={{ color: 'red' }}>Error!</h2>
        <p>{error}</p>
        <button onClick={() => setUserId(userId)}>Retry</button>
      </div>
    );
  }

  // Success state
  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>User Profile</h2>
      
      {user && (
        <div style={{ border: '2px solid #ddd', borderRadius: '8px', padding: '20px' }}>
          <h3>{user.name}</h3>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Phone:</strong> {user.phone}</p>
          <p><strong>Website:</strong> {user.website}</p>
          
          <div style={{ marginTop: '20px' }}>
            <h4>Address:</h4>
            <p>{user.address.street}, {user.address.suite}</p>
            <p>{user.address.city}, {user.address.zipcode}</p>
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <h4>Company:</h4>
            <p><strong>{user.company.name}</strong></p>
            <p style={{ fontStyle: 'italic' }}>"{user.company.catchPhrase}"</p>
          </div>
        </div>
      )}

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => setUserId(prev => Math.max(1, prev - 1))}
          disabled={userId === 1}
        >
          Previous User
        </button>
        <button 
          onClick={() => setUserId(prev => Math.min(10, prev + 1))}
          disabled={userId === 10}
        >
          Next User
        </button>
        <button onClick={() => setUserId(userId)}>
          Refresh
        </button>
      </div>
      
      <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
        Current User ID: {userId}
      </p>
    </div>
  );
}

export default UserFetcher;
```

## ✅ Acceptance Criteria
- [ ] Shows loading state initially
- [ ] Fetches user data on mount
- [ ] Displays all user information
- [ ] Previous/Next buttons fetch different users
- [ ] Refresh button refetches current user
- [ ] Loading state shows during each fetch
- [ ] Error handling works (test with invalid ID)
- [ ] useEffect has correct dependencies

## 🐛 Edge Cases
- What if the API is slow? (Should show loading)
- What if the API fails? (Should show error)
- What if userId changes before previous request finishes? (Race condition - we'll learn about abort in advanced topics)

## 📋 Self-Review Checklist
- [ ] Used `fetch` to get data
- [ ] Handled loading state (before and after fetch)
- [ ] Handled error state (catch block)
- [ ] Handled success state (set user data)
- [ ] useEffect has `[userId]` as dependency
- [ ] No infinite loops
- [ ] UI shows correct state at each stage

## 💡 Complete Solution

```jsx
useEffect(() => {
  setLoading(true);
  setError(null);

  fetch(`https://jsonplaceholder.typicode.com/users/${userId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return response.json();
    })
    .then(data => {
      setUser(data);
      setLoading(false);
    })
    .catch(err => {
      setError(err.message);
      setLoading(false);
    });

}, [userId]); // Re-run when userId changes
```

## 💡 Bonus Challenges

1. **Add abort controller** to cancel previous requests:
```jsx
useEffect(() => {
  const controller = new AbortController();
  
  fetch(url, { signal: controller.signal })
    .then(...)
    .catch(err => {
      if (err.name === 'AbortError') return;
      setError(err.message);
    });
    
  return () => controller.abort();
}, [userId]);
```

2. **Add a search feature** to find users by name
3. **Cache fetched users** to avoid refetching
4. **Add loading skeleton** instead of just text

---

**Time limit:** 20 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to the Interview Question!
