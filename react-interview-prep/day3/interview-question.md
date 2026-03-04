# Day 3 Interview Question

## ❓ Question

**Interviewer asks:**

> "I'm building a login form in React. I want the submit button to be disabled while the form is submitting, and show a loading message. After submission, I want to show either a success or error message. Can you write this component and explain your approach?"

**Additional requirements:**
- Email and password fields (controlled)
- Submit button shows "Login" or "Logging in..." based on state
- Button is disabled while submitting
- After submission, show success or error message
- Form should not reload the page

---

## 📝 Your Task

Write the complete component with:
1. **Proper controlled inputs** (email, password)
2. **Loading state** (isLoading)
3. **Submit handler** with e.preventDefault()
4. **Conditional rendering** for button text and messages
5. **Disabled state** for the button

Also explain:
- Why you made it a controlled component
- Why you need e.preventDefault()
- How you handle the loading state

---

## ✅ Evaluation Criteria

Your code should include:
- [ ] Controlled email and password inputs
- [ ] Loading state management
- [ ] Button disabled during submission
- [ ] Conditional button text
- [ ] Success/error message display
- [ ] e.preventDefault() in form handler
- [ ] Clean code structure

Your explanation should cover:
- [ ] Why controlled components are better
- [ ] Purpose of preventDefault
- [ ] State management strategy

---

## 🎯 Model Answer (Don't peek until you've tried!)

<details>
<summary>Click to reveal answer</summary>

### Code Solution:

```jsx
import { useState } from 'react';

function LoginForm() {
  // Form field states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // UI states
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: 'message' }

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload
    
    // Reset previous messages
    setMessage(null);
    setIsLoading(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Simulate success (in real app, this would be actual API call)
      if (email && password) {
        setMessage({ type: 'success', text: 'Login successful!' });
        // Clear form
        setEmail('');
        setPassword('');
      } else {
        throw new Error('Please fill all fields');
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '40px auto', padding: '20px' }}>
      <h2>Login</h2>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Email:
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            style={{ width: '100%', padding: '8px' }}
            required
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Password:
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            style={{ width: '100%', padding: '8px' }}
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: isLoading ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      {/* Conditional message display */}
      {message && (
        <div
          style={{
            marginTop: '20px',
            padding: '15px',
            borderRadius: '4px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
          }}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}

export default LoginForm;
```

### Explanation:

#### 1. Why Controlled Components?
- **Single source of truth:** React state controls the input values
- **Easy validation:** Can validate on every keystroke
- **Easy to clear:** Just reset state to clear inputs
- **Predictable:** We always know the current value
- **Enables features:** Easy to add features like "show password" toggle

#### 2. Why e.preventDefault()?
- Prevents default form submission behavior (page reload)
- In traditional HTML, forms reload the page and send data to server
- In React, we want to handle everything in JavaScript
- Without it, the page would refresh and lose all state

#### 3. State Management Strategy:
- **Form data states:** `email`, `password` - track user input
- **UI state:** `isLoading` - track submission status
- **Message state:** `message` - track success/error feedback
- **Separation of concerns:** Each state has a clear purpose

#### 4. Key Patterns Used:

**Conditional Rendering:**
```jsx
{isLoading ? 'Logging in...' : 'Login'}  // Button text
{message && <div>...</div>}              // Message display
```

**Disabled State:**
```jsx
disabled={isLoading}  // On button and inputs
```

**Controlled Inputs:**
```jsx
value={email}
onChange={(e) => setEmail(e.target.value)}
```

**Form Submission:**
```jsx
<form onSubmit={handleSubmit}>
  // e.preventDefault() prevents reload
  // async/await for API calls
  // try/catch for error handling
  // finally to reset loading state
</form>
```

### Interview Tips:

When explaining this solution in an interview:

1. **Start with the big picture:** "I'll use controlled components for the form inputs and manage loading/message states"

2. **Explain as you code:** "I'm using controlled inputs because..." (don't just write code silently)

3. **Mention edge cases:** "I'm disabling inputs during submission to prevent changes mid-request"

4. **Show you understand async:** "In a real app, this would be an API call with proper error handling"

5. **Talk about UX:** "I'm showing loading state so users know something is happening"

</details>

---

## 💬 When You're Ready

Write your solution and explanation, then paste here for review. I'll evaluate:
- Code correctness and completeness
- State management approach
- Understanding of controlled components
- Interview communication quality

**Remember:** In interviews, explaining your thought process is as important as writing correct code!
