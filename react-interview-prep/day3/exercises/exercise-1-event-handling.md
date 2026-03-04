# Exercise 1: Event Handling (10 mins)

## 🎯 Goal
Practice handling different types of events in React.

## 📝 Instructions

Create a `EventDemo.jsx` component that demonstrates different event handlers:

1. **Click button** - Shows a count of how many times it was clicked
2. **Hover div** - Changes background color on mouse enter/leave
3. **Keyboard input** - Displays the last key pressed

**Starter code:**
```jsx
import { useState } from 'react';

function EventDemo() {
  const [clickCount, setClickCount] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [lastKey, setLastKey] = useState('');

  return (
    <div style={{ padding: '20px' }}>
      <h2>Event Handling Demo</h2>
      
      {/* Click Counter */}
      <div>
        <button onClick={/* TODO */}>
          Clicked {clickCount} times
        </button>
      </div>
      
      {/* Hover Area */}
      <div
        onMouseEnter={/* TODO */}
        onMouseLeave={/* TODO */}
        style={{
          width: '200px',
          height: '100px',
          backgroundColor: /* TODO: change based on isHovered */,
          border: '2px solid black',
          marginTop: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {isHovered ? 'Hovering!' : 'Hover over me'}
      </div>
      
      {/* Keyboard Input */}
      <div style={{ marginTop: '20px' }}>
        <input
          type="text"
          placeholder="Type something..."
          onKeyDown={/* TODO: capture e.key */}
        />
        <p>Last key pressed: {lastKey || 'None'}</p>
      </div>
    </div>
  );
}

export default EventDemo;
```

## ✅ Acceptance Criteria
- [ ] Click button increments count
- [ ] Hover area changes color on mouse enter/leave
- [ ] Keyboard input displays last key pressed
- [ ] No console errors
- [ ] State updates correctly for all events

## 🐛 Edge Cases
- What happens if you rapidly click the button? (Should handle fine)
- What if you hold down a key? (Should keep updating)

## 📋 Self-Review Checklist
- [ ] Event handlers don't call functions immediately (no parentheses)
- [ ] Used correct camelCase event names
- [ ] State updates trigger re-renders
- [ ] Background color changes are visible

## 💡 Hints

**Click handler:**
```jsx
onClick={() => setClickCount(clickCount + 1)}
```

**Hover handlers:**
```jsx
onMouseEnter={() => setIsHovered(true)}
onMouseLeave={() => setIsHovered(false)}
```

**Keyboard handler:**
```jsx
onKeyDown={(e) => setLastKey(e.key)}
```

**Conditional background:**
```jsx
backgroundColor: isHovered ? 'lightblue' : 'lightgray'
```

---

**Time limit:** 10 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 2!
