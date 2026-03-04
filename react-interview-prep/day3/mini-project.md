# Day 3 Mini-Project: Interactive Counter + Form Validator

## 🎯 Goal
Build a multi-feature application combining everything from Day 3: events, controlled components, and conditional rendering.

**Time:** 30-60 minutes

---

## 📋 Requirements

Build an app with TWO main features:

### Feature 1: Advanced Counter
- Increment, Decrement, Reset buttons
- Input field to set counter to a specific value
- Visual indicator when counter is positive, negative, or zero (different colors)
- History of last 5 actions

### Feature 2: Contact Form with Validation
- Name, Email, Message fields
- Real-time validation messages
- Submit button (disabled unless form is valid)
- Success confirmation after submission

---

## ✅ Acceptance Criteria

**Counter:**
- [ ] Three buttons work correctly
- [ ] Input allows setting custom counter value
- [ ] Color changes based on counter value (green > 0, red < 0, gray = 0)
- [ ] Shows last 5 actions (e.g., "+1", "-1", "Reset", "Set to 10")

**Form:**
- [ ] All three fields are controlled
- [ ] Real-time validation messages appear
- [ ] Submit button disabled when form invalid
- [ ] Success message shows after submission
- [ ] Form clears after successful submission

**General:**
- [ ] No console errors
- [ ] Clean, organized code
- [ ] Good user experience

---

## 🐛 Edge Cases to Handle

1. **Counter input:**
   - Empty input
   - Non-numeric input
   - Very large numbers

2. **Form validation:**
   - Empty fields
   - Invalid email format
   - Message too short (min 10 characters)

3. **History:**
   - Max 5 items (remove oldest when adding 6th)

---

## 📁 File Structure

```
day3/
  mini-project/
    Counter.jsx
    ContactForm.jsx
    App.jsx
    App.css
```

---

## 💡 Starter Code

**Counter.jsx:**
```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [history, setHistory] = useState([]);

  const addToHistory = (action) => {
    // TODO: Add action to history (keep max 5)
    // Use: setHistory(prev => [action, ...prev].slice(0, 5))
  };

  const handleIncrement = () => {
    setCount(count + 1);
    addToHistory('+1');
  };

  const handleDecrement = () => {
    // TODO: Implement
  };

  const handleReset = () => {
    // TODO: Implement
  };

  const handleSetValue = () => {
    // TODO: Validate inputValue is a number
    // TODO: Set count to that value
    // TODO: Add to history
    // TODO: Clear input
  };

  // TODO: Determine color based on count
  const getColor = () => {
    if (count > 0) return 'green';
    if (count < 0) return 'red';
    return 'gray';
  };

  return (
    <div style={{ padding: '20px', border: '2px solid #ddd', borderRadius: '8px', marginBottom: '20px' }}>
      <h2>Advanced Counter</h2>
      
      <div style={{ 
        fontSize: '48px', 
        fontWeight: 'bold', 
        color: getColor(),
        textAlign: 'center',
        margin: '20px 0'
      }}>
        {count}
      </div>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '20px' }}>
        <button onClick={handleIncrement}>+ Increment</button>
        <button onClick={handleDecrement}>- Decrement</button>
        <button onClick={handleReset}>Reset</button>
      </div>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '20px' }}>
        <input
          type="number"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Set value..."
          style={{ padding: '8px' }}
        />
        <button onClick={handleSetValue}>Set</button>
      </div>

      {history.length > 0 && (
        <div>
          <h3>History (Last 5 actions):</h3>
          <ul>
            {history.map((action, index) => (
              <li key={index}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Counter;
```

**ContactForm.jsx:**
```jsx
import { useState } from 'react';

function ContactForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  // Validation logic
  const isNameValid = name.trim().length >= 2;
  const isEmailValid = email.includes('@') && email.includes('.');
  const isMessageValid = message.trim().length >= 10;
  
  const isFormValid = isNameValid && isEmailValid && isMessageValid;

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!isFormValid) return;
    
    // Simulate submission
    console.log({ name, email, message });
    
    // Show success message
    setSubmitted(true);
    
    // Clear form
    setName('');
    setEmail('');
    setMessage('');
    
    // Hide success message after 3 seconds
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div style={{ padding: '20px', border: '2px solid #ddd', borderRadius: '8px' }}>
      <h2>Contact Form</h2>

      {submitted && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#d4edda', 
          color: '#155724',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          ✓ Message sent successfully!
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Name:
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          />
          {/* TODO: Show error if name touched and invalid */}
          {name && !isNameValid && (
            <p style={{ color: 'red', fontSize: '14px', margin: '5px 0 0 0' }}>
              Name must be at least 2 characters
            </p>
          )}
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Email:
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          />
          {/* TODO: Show error if email touched and invalid */}
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Message (min 10 characters):
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows="4"
            style={{ width: '100%', padding: '8px' }}
          />
          {/* TODO: Show error if message touched and invalid */}
          {/* TODO: Show character count */}
          <p style={{ fontSize: '12px', color: '#666', margin: '5px 0 0 0' }}>
            {message.length} characters
          </p>
        </div>

        <button
          type="submit"
          disabled={!isFormValid}
          style={{
            padding: '10px 20px',
            backgroundColor: isFormValid ? '#4CAF50' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isFormValid ? 'pointer' : 'not-allowed'
          }}
        >
          Submit
        </button>
      </form>
    </div>
  );
}

export default ContactForm;
```

**App.jsx:**
```jsx
import Counter from './Counter';
import ContactForm from './ContactForm';
import './App.css';

function App() {
  return (
    <div className="app">
      <h1 style={{ textAlign: 'center' }}>Day 3 Mini-Project</h1>
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <Counter />
        <ContactForm />
      </div>
    </div>
  );
}

export default App;
```

---

## 📋 Implementation Checklist

**Counter:**
- [ ] Increment/Decrement work
- [ ] Reset sets to 0
- [ ] Custom value input works
- [ ] Input validation (numbers only)
- [ ] Color changes based on value
- [ ] History tracks last 5 actions
- [ ] History uses array index as key (OK here since static order)

**Contact Form:**
- [ ] All inputs are controlled
- [ ] Real-time validation errors show
- [ ] Email validation checks for @ and .
- [ ] Message validation checks length
- [ ] Submit disabled when invalid
- [ ] Success message appears
- [ ] Form clears after submit
- [ ] Success message auto-hides

---

## 🎨 Bonus Challenges

1. **Counter:**
   - Add step size input (increment by 2, 5, 10, etc.)
   - Add min/max boundaries
   - Keyboard shortcuts (arrow up/down)

2. **Form:**
   - Add password field with strength indicator
   - Add checkbox for "agree to terms" (required)
   - Save draft to localStorage

3. **Both:**
   - Add smooth animations (CSS transitions)
   - Make it responsive (looks good on mobile)
   - Add dark mode toggle

---

## 📤 Submission

When ready, paste your code for review. I'll evaluate:
- ✅ Event handling correctness
- ✅ Controlled component implementation
- ✅ Conditional rendering patterns
- ✅ Validation logic
- ✅ State management
- ✅ Code quality and organization
- ✅ User experience

**Remember:** This combines all Day 3 concepts - make it count! 🚀
