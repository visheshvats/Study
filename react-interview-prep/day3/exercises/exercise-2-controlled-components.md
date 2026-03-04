# Exercise 2: Controlled Components (15 mins)

## 🎯 Goal
Build a form with controlled inputs.

## 📝 Instructions

Create a `RegistrationForm.jsx` component with:
- Name input (text)
- Email input (email)
- Age input (number)
- Submit button
- Display the form data below when submitted

**Starter code:**
```jsx
import { useState } from 'react';

function RegistrationForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    // TODO: Prevent default form behavior
    // TODO: Set submitted to true
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px' }}>
      <h2>Registration Form</h2>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label>
            Name:
            <input
              type="text"
              value={/* TODO */}
              onChange={/* TODO */}
              style={{ marginLeft: '10px', padding: '5px' }}
            />
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Email:
            <input
              type="email"
              value={/* TODO */}
              onChange={/* TODO */}
              style={{ marginLeft: '10px', padding: '5px' }}
            />
          </label>
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <label>
            Age:
            <input
              type="number"
              value={/* TODO */}
              onChange={/* TODO */}
              style={{ marginLeft: '10px', padding: '5px' }}
            />
          </label>
        </div>
        
        <button type="submit" style={{ padding: '10px 20px' }}>
          Register
        </button>
      </form>

      {/* TODO: Show this only if submitted === true */}
      {submitted && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
          <h3>Submitted Data:</h3>
          <p><strong>Name:</strong> {name}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Age:</strong> {age}</p>
        </div>
      )}
    </div>
  );
}

export default RegistrationForm;
```

## ✅ Acceptance Criteria
- [ ] All three inputs are controlled by state
- [ ] onChange handlers update respective state
- [ ] Form submission prevents page reload
- [ ] Submitted data displays after form submission
- [ ] Inputs reflect what user types immediately
- [ ] No console warnings

## 🐛 Edge Cases
- What if user submits with empty fields? (Allow for now, we'll add validation later)
- What if user types in age input? (Should only accept numbers)

## 📋 Self-Review Checklist
- [ ] Each input has both `value` and `onChange`
- [ ] Used `e.preventDefault()` in handleSubmit
- [ ] State updates when typing in inputs
- [ ] Conditional rendering works with `&&`
- [ ] Form data displays correctly after submit

## 💡 Bonus Challenges

1. **Add validation:**
```jsx
const handleSubmit = (e) => {
  e.preventDefault();
  
  if (!name || !email || !age) {
    alert('Please fill all fields');
    return;
  }
  
  if (age < 18) {
    alert('Must be 18 or older');
    return;
  }
  
  setSubmitted(true);
};
```

2. **Add a reset button** that clears all fields and hides submitted data

3. **Show character count** for the name field (e.g., "Characters: 5/50")

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 3!
