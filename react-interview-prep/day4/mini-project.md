# Day 4 Mini-Project: GitHub User Search

## 🎯 Goal
Build a real-world data fetching application that searches GitHub users using their API.

**Time:** 30-60 minutes

---

## 📋 Requirements

Build a GitHub User Search app with:

### Core Features:
1. **Search input** - Type GitHub username
2. **Debounced search** - Don't search on every keystroke (wait 500ms)
3. **Loading states** - Show spinner while searching
4. **Error handling** - Handle "user not found" and network errors
5. **User display** - Show avatar, name, bio, followers, repos, etc.
6. **Proper cleanup** - Abort pending requests

### API Endpoint:
```
https://api.github.com/users/{username}
```

---

## ✅ Acceptance Criteria

- [ ] Search input is controlled
- [ ] Search is debounced (waits 500ms after typing stops)
- [ ] Shows loading state while fetching
- [ ] Displays user data nicely when found
- [ ] Shows error message when user not found
- [ ] Handles network errors gracefully
- [ ] Properly aborts previous requests
- [ ] No memory leaks
- [ ] Clean, organized code

---

## 🐛 Edge Cases to Handle

1. **Empty search** - Don't fetch when input is empty
2. **Rapid typing** - Debounce to avoid too many requests
3. **User not found** - Handle 404 errors
4. **Network failure** - Handle fetch errors
5. **Component unmount** - Abort pending requests
6. **Race conditions** - Cancel old requests when new search starts

---

## 📁 File Structure

```
day4/
  mini-project/
    GitHubUserSearch.jsx
    GitHubUserSearch.css
    App.jsx
```

---

## 💡 Starter Code

**GitHubUserSearch.jsx:**
```jsx
import { useState, useEffect } from 'react';
import './GitHubUserSearch.css';

function GitHubUserSearch() {
  const [username, setUsername] = useState('');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debouncedUsername, setDebouncedUsername] = useState('');

  // TODO: Debounce effect
  // Wait 500ms after user stops typing, then update debouncedUsername
  useEffect(() => {
    const timerId = setTimeout(() => {
      // Update debouncedUsername after delay
    }, 500);

    // Cleanup: Clear timeout if username changes before 500ms
    return () => {
      // Clear the timeout
    };
  }, [/* dependencies? */]);

  // TODO: Fetch effect
  // Fetch user when debouncedUsername changes
  useEffect(() => {
    // Don't fetch if username is empty
    if (!debouncedUsername) {
      setUser(null);
      setError(null);
      return;
    }

    const controller = new AbortController();
    
    setLoading(true);
    setError(null);

    fetch(`https://api.github.com/users/${debouncedUsername}`, {
      signal: controller.signal
    })
      .then(response => {
        if (response.status === 404) {
          throw new Error('User not found');
        }
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
        if (err.name === 'AbortError') return;
        // TODO: Set error message
        // TODO: Set loading to false
        // TODO: Clear user data
      });

    // TODO: Cleanup function
    return () => {
      // Abort the fetch
    };
  }, [/* dependencies? */]);

  return (
    <div className="search-container">
      <h1>🔍 GitHub User Search</h1>
      
      <div className="search-box">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter GitHub username (e.g., octocat)..."
          className="search-input"
        />
        {loading && <div className="loading-icon">⏳</div>}
      </div>

      {error && (
        <div className="error-message">
          <h3>❌ {error}</h3>
          <p>Try another username</p>
        </div>
      )}

      {user && !loading && (
        <div className="user-card">
          <img src={user.avatar_url} alt={user.login} className="avatar" />
          
          <div className="user-info">
            <h2>{user.name || user.login}</h2>
            <p className="username">@{user.login}</p>
            
            {user.bio && <p className="bio">{user.bio}</p>}
            
            <div className="stats">
              <div className="stat">
                <span className="stat-value">{user.public_repos}</span>
                <span className="stat-label">Repos</span>
              </div>
              <div className="stat">
                <span className="stat-value">{user.followers}</span>
                <span className="stat-label">Followers</span>
              </div>
              <div className="stat">
                <span className="stat-value">{user.following}</span>
                <span className="stat-label">Following</span>
              </div>
            </div>

            <div className="details">
              {user.location && <p>📍 {user.location}</p>}
              {user.blog && <p>🔗 <a href={user.blog} target="_blank" rel="noopener noreferrer">{user.blog}</a></p>}
              {user.twitter_username && <p>🐦 @{user.twitter_username}</p>}
            </div>

            <a 
              href={user.html_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="profile-link"
            >
              View GitHub Profile
            </a>
          </div>
        </div>
      )}

      {!user && !loading && !error && username && (
        <div className="empty-state">
          <p>Searching for "{username}"...</p>
        </div>
      )}
    </div>
  );
}

export default GitHubUserSearch;
```

**GitHubUserSearch.css:**
```css
.search-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.search-box {
  position: relative;
  margin-bottom: 30px;
}

.search-input {
  width: 100%;
  padding: 15px 50px 15px 15px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #0366d6;
}

.loading-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
}

.error-message {
  text-align: center;
  padding: 30px;
  background-color: #ffe6e6;
  border-radius: 8px;
  color: #c0392b;
}

.user-card {
  display: flex;
  gap: 30px;
  padding: 30px;
  border: 2px solid #e1e4e8;
  border-radius: 12px;
  background-color: #f6f8fa;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 3px solid #0366d6;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 5px 0;
  color: #24292e;
}

.username {
  color: #586069;
  margin: 0 0 15px 0;
}

.bio {
  color: #24292e;
  margin-bottom: 20px;
}

.stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #0366d6;
}

.stat-label {
  font-size: 14px;
  color: #586069;
}

.details {
  margin-bottom: 20px;
}

.details p {
  margin: 5px 0;
  color: #586069;
}

.details a {
  color: #0366d6;
  text-decoration: none;
}

.details a:hover {
  text-decoration: underline;
}

.profile-link {
  display: inline-block;
  padding: 10px 20px;
  background-color: #0366d6;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.profile-link:hover {
  background-color: #0256c7;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}
```

---

## 📋 Implementation Checklist

**Debounce Effect:**
- [ ] setTimeout to delay updating debouncedUsername
- [ ] Cleanup clears timeout
- [ ] Dependencies: `[username]`

**Fetch Effect:**
- [ ] Checks if debouncedUsername is empty
- [ ] Uses AbortController
- [ ] Handles 404 (user not found)
- [ ] Handles network errors
- [ ] Updates all states correctly
- [ ] Cleanup aborts fetch
- [ ] Dependencies: `[debouncedUsername]`

**UI:**
- [ ] Shows loading while fetching
- [ ] Displays all user information
- [ ] Error state looks good
- [ ] Responsive design

---

## 💡 Complete Solution

**Debounce effect:**
```jsx
useEffect(() => {
  const timerId = setTimeout(() => {
    setDebouncedUsername(username);
  }, 500);

  return () => clearTimeout(timerId);
}, [username]);
```

**Fetch effect:**
```jsx
useEffect(() => {
  if (!debouncedUsername) {
    setUser(null);
    setError(null);
    return;
  }

  const controller = new AbortController();
  
  setLoading(true);
  setError(null);

  fetch(`https://api.github.com/users/${debouncedUsername}`, {
    signal: controller.signal
  })
    .then(response => {
      if (response.status === 404) {
        throw new Error('User not found');
      }
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
      if (err.name === 'AbortError') return;
      setError(err.message);
      setLoading(false);
      setUser(null);
    });

  return () => controller.abort();
}, [debouncedUsername]);
```

---

## 🎨 Bonus Challenges

1. **Add repository list** - Fetch and display user's repos
2. **Add search history** - Save recent searches in localStorage
3. **Add favorites** - Let users save favorite profiles
4. **Add comparison** - Compare two GitHub users side-by-side
5. **Add dark mode** - Toggle between light/dark themes

---

## 📤 Submission

When ready, paste your code for review. I'll check:
- ✅ Proper useEffect usage and dependencies
- ✅ Cleanup implementation (abort + timeout)
- ✅ Debouncing logic
- ✅ Error handling
- ✅ Loading states
- ✅ Code quality and organization
- ✅ User experience

**This is a real interview-level project!** Understanding debouncing, cleanup, and race conditions is crucial. 🚀
