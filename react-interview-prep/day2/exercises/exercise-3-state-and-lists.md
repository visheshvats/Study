# Exercise 3: State + Lists Combined (15 mins)

## 🎯 Goal
Combine state and list rendering to build a dynamic list that can be modified.

## 📝 Instructions

Create a `ColorPicker.jsx` component that:
- Has state to track which color is selected
- Displays a list of color options as buttons
- Shows the currently selected color
- Changes background when a color is clicked

**Starter code:**
```jsx
import { useState } from 'react';

function ColorPicker() {
  const colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange'];
  
  // TODO: Add state for selected color (start with 'red')
  
  return (
    <div>
      <h2>Color Picker</h2>
      <div className="selected-color" style={{ 
        backgroundColor: /* selected color here */,
        width: '200px',
        height: '200px',
        border: '2px solid black'
      }}>
        {/* Display selected color name */}
      </div>
      
      <div className="color-buttons">
        {/* TODO: Map over colors and create a button for each */}
        {/* When clicked, update the selected color */}
      </div>
    </div>
  );
}

export default ColorPicker;
```

Expected button structure:
```jsx
<button 
  key={color} 
  onClick={() => setSelectedColor(color)}
>
  {color}
</button>
```

## ✅ Acceptance Criteria
- [ ] State tracks the currently selected color
- [ ] All colors are rendered as buttons
- [ ] Clicking a button updates the selected color
- [ ] The colored box changes to match the selected color
- [ ] Selected color name is displayed
- [ ] Each button has a unique key

## 🐛 Edge Cases
- What if colors array is empty? (Show a message: "No colors available")
- Bonus: Highlight the currently selected button with different styling

## 📋 Self-Review Checklist
- [ ] useState is used correctly
- [ ] .map() renders all color buttons
- [ ] Each button has proper key (using color name)
- [ ] onClick handlers update state correctly
- [ ] Background color updates when clicking buttons

## 💡 Bonus Challenges

1. **Highlight active button:**
```jsx
<button 
  key={color}
  onClick={() => setSelectedColor(color)}
  style={{
    backgroundColor: selectedColor === color ? color : 'white',
    color: selectedColor === color ? 'white' : 'black',
    border: '2px solid black',
    padding: '10px 20px',
    margin: '5px',
    cursor: 'pointer'
  }}
>
  {color}
</button>
```

2. **Add a reset button** that sets color back to the first one

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐⭐

Once done, move to the Interview Question!
