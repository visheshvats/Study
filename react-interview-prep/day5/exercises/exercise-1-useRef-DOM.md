# Exercise 1: useRef for DOM Access (10 mins)

## 🎯 Goal
Practice using useRef to interact with DOM elements.

## 📝 Instructions

Create a `FocusManager.jsx` component with:
- Text input field
- "Focus Input" button that focuses the input
- "Scroll to Bottom" button that scrolls a div to bottom
- "Measure Element" button that logs element dimensions

**Starter code:**
```jsx
import { useRef } from 'react';

function FocusManager() {
  // TODO: Create refs
  const inputRef = useRef(null);
  const divRef = useRef(null);

  const handleFocusInput = () => {
    // TODO: Focus the input
  };

  const handleScrollToBottom = () => {
    // TODO: Scroll div to bottom
  };

  const handleMeasureDiv = () => {
    // TODO: Log div dimensions (width, height)
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>useRef DOM Demo</h2>
      
      {/* Input Section */}
      <div style={{ marginBottom: '20px' }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="This can be focused programmatically"
          style={{ padding: '10px', width: '300px' }}
        />
        <button onClick={handleFocusInput} style={{ marginLeft: '10px' }}>
          Focus Input
        </button>
      </div>

      {/* Scrollable Div Section */}
      <div
        ref={divRef}
        style={{
          height: '200px',
          width: '400px',
          overflow: 'auto',
          border: '2px solid #ddd',
          padding: '10px',
          marginBottom: '10px'
        }}
      >
        <h3>Scrollable Content</h3>
        {Array.from({ length: 50 }, (_, i) => (
          <p key={i}>Line {i + 1}</p>
        ))}
      </div>
      
      <button onClick={handleScrollToBottom} style={{ marginRight: '10px' }}>
        Scroll to Bottom
      </button>
      <button onClick={handleMeasureDiv}>
        Measure Div
      </button>
    </div>
  );
}

export default FocusManager;
```

## ✅ Acceptance Criteria
- [ ] Input ref is created with useRef
- [ ] Div ref is created with useRef
- [ ] "Focus Input" button focuses the input
- [ ] "Scroll to Bottom" scrolls div to bottom
- [ ] "Measure Div" logs dimensions to console
- [ ] No errors in console

## 🐛 Edge Cases
- What if you click "Focus Input" before the component mounts?
- What if the div has no content to scroll?

## 📋 Self-Review Checklist
- [ ] Created refs with `useRef(null)`
- [ ] Attached refs with `ref={refName}`
- [ ] Accessed DOM with `refName.current`
- [ ] Used correct DOM methods (focus, scrollTop, getBoundingClientRect)

## 💡 Complete Solution

```jsx
const handleFocusInput = () => {
  inputRef.current?.focus(); // Optional chaining for safety
};

const handleScrollToBottom = () => {
  if (divRef.current) {
    divRef.current.scrollTop = divRef.current.scrollHeight;
  }
};

const handleMeasureDiv = () => {
  if (divRef.current) {
    const { width, height } = divRef.current.getBoundingClientRect();
    console.log(`Div dimensions: ${width}px × ${height}px`);
  }
};
```

## 💡 Bonus Challenges

1. **Add auto-scroll** - Automatically scroll to bottom when new content is added
2. **Highlight on focus** - Add border color when input is focused
3. **Smooth scroll** - Use `scrollIntoView({ behavior: 'smooth' })`

---

**Time limit:** 10 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 2!
