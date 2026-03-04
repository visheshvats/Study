# Exercise 3: Conditional Rendering (15 mins)

## 🎯 Goal
Practice different conditional rendering patterns.

## 📝 Instructions

Create a `StatusDisplay.jsx` component that shows different UI based on state:

**States:**
- Loading (show spinner/message)
- Error (show error message)
- Success (show data)
- Empty (no data available)

**Starter code:**
```jsx
import { useState } from 'react';

function StatusDisplay() {
  const [status, setStatus] = useState('idle'); // idle, loading, success, error, empty
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const simulateLoading = () => {
    setStatus('loading');
    setData(null);
    setError(null);
    
    // Simulate API call
    setTimeout(() => {
      setStatus('success');
      setData({ name: 'John Doe', age: 30 });
    }, 2000);
  };

  const simulateError = () => {
    setStatus('loading');
    setData(null);
    setError(null);
    
    setTimeout(() => {
      setStatus('error');
      setError('Failed to load data. Please try again.');
    }, 1500);
  };

  const simulateEmpty = () => {
    setStatus('empty');
    setData(null);
    setError(null);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Conditional Rendering Demo</h2>
      
      {/* Control buttons */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={simulateLoading} style={{ marginRight: '10px' }}>
          Load Data
        </button>
        <button onClick={simulateError} style={{ marginRight: '10px' }}>
          Simulate Error
        </button>
        <button onClick={simulateEmpty}>
          Show Empty
        </button>
      </div>

      {/* TODO: Conditionally render based on status */}
      <div style={{ padding: '20px', border: '2px solid #ddd', borderRadius: '8px', minHeight: '100px' }}>
        {/* Show loading state */}
        {status === 'loading' && (
          <div style={{ textAlign: 'center' }}>
            <p>Loading...</p>
            <div className="spinner">⏳</div>
          </div>
        )}

        {/* TODO: Show error state */}
        
        {/* TODO: Show success state with data */}
        
        {/* TODO: Show empty state */}
        
        {/* TODO: Show idle state (initial) */}
      </div>
    </div>
  );
}

export default StatusDisplay;
```

## ✅ Acceptance Criteria
- [ ] Shows loading message when status is 'loading'
- [ ] Shows error message when status is 'error'
- [ ] Shows user data when status is 'success'
- [ ] Shows "No data" message when status is 'empty'
- [ ] Shows initial message when status is 'idle'
- [ ] Buttons correctly trigger state changes
- [ ] Only ONE state displays at a time

## 🐛 Edge Cases
- Ensure only one state shows at a time
- Make sure previous data clears when loading new state

## 📋 Self-Review Checklist
- [ ] Used conditional rendering (&&, ternary, or if statements)
- [ ] Each state displays unique content
- [ ] No multiple states showing simultaneously
- [ ] Button clicks update the status correctly

## 💡 Complete Solution

All the conditional rendering blocks:

```jsx
{/* Loading */}
{status === 'loading' && (
  <div style={{ textAlign: 'center' }}>
    <p>Loading...</p>
    <div>⏳</div>
  </div>
)}

{/* Error */}
{status === 'error' && (
  <div style={{ color: 'red' }}>
    <h3>Error!</h3>
    <p>{error}</p>
    <button onClick={simulateLoading}>Retry</button>
  </div>
)}

{/* Success */}
{status === 'success' && data && (
  <div style={{ color: 'green' }}>
    <h3>Success!</h3>
    <p><strong>Name:</strong> {data.name}</p>
    <p><strong>Age:</strong> {data.age}</p>
  </div>
)}

{/* Empty */}
{status === 'empty' && (
  <div style={{ textAlign: 'center', color: '#999' }}>
    <p>No data available</p>
  </div>
)}

{/* Idle */}
{status === 'idle' && (
  <div style={{ textAlign: 'center', color: '#666' }}>
    <p>Click a button to load data</p>
  </div>
)}
```

## 💡 Bonus Challenges

1. **Use early return pattern instead:**
```jsx
const renderContent = () => {
  if (status === 'loading') return <div>Loading...</div>;
  if (status === 'error') return <div>{error}</div>;
  if (status === 'success') return <div>{data.name}</div>;
  if (status === 'empty') return <div>No data</div>;
  return <div>Click a button</div>;
};

return (
  <div>
    {/* buttons */}
    <div>{renderContent()}</div>
  </div>
);
```

2. **Add a progress bar** during loading state

3. **Add animations** when states change (CSS transitions)

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to the Interview Question!
