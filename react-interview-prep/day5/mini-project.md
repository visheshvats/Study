# Day 5 Mini-Project: Debounced Search with Optimizations

## 🎯 Goal
Build an optimized, real-world search component with debouncing, filtering, and proper use of useRef, useMemo, and useCallback.

**Time:** 30-60 minutes

---

## 📋 Requirements

Build a Product Search application with:

### Core Features:
1. **Debounced search** - Wait 300ms after typing stops
2. **Filter large dataset** - 1000+ products
3. **Multiple filters** - By category, price range, rating
4. **Optimizations** - useMemo, useCallback, React.memo
5. **Search stats** - Show search count, render count, filter time

### Performance Goals:
- Typing feels instant (debounced API calls)
- Filtering is fast (< 50ms for 1000 items)
- No unnecessary re-renders

---

## ✅ Acceptance Criteria

- [ ] Search input is debounced (300ms delay)
- [ ] Filters use useMemo for performance
- [ ] Product cards use React.memo
- [ ] Stats show render count (useRef)
- [ ] Measure and display filter duration
- [ ] No unnecessary child re-renders
- [ ] Clean, organized code

---

## 📁 File Structure

```
day5/
  mini-project/
    ProductSearch.jsx
    ProductCard.jsx
    generateProducts.js
    ProductSearch.css
    App.jsx
```

---

## 💡 Starter Code

**generateProducts.js:**
```js
// Generate mock product data
export function generateProducts(count = 1000) {
  const categories = ['Electronics', 'Clothing', 'Food',' Books', 'Toys'];
  const products = [];
  
  for (let i = 1; i <= count; i++) {
    products.push({
      id: i,
      name: `Product ${i}`,
      category: categories[Math.floor(Math.random() * categories.length)],
      price: Math.floor(Math.random() * 1000) + 10,
      rating: (Math.random() * 5).toFixed(1),
      description: `Description for product ${i}`
    });
  }
  
  return products;
}
```

**ProductCard.jsx:**
```jsx
import React from 'react';

// Memoized to prevent unnecessary re-renders
const ProductCard = React.memo(({ product, onAddToCart }) => {
  console.log(`Rendering ProductCard: ${product.id}`);
  
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p className="category">{product.category}</p>
      <p className="price">${product.price}</p>
      <p className="rating">⭐ {product.rating}</p>
      <p className="description">{product.description}</p>
      <button onClick={() => onAddToCart(product.id)}>
        Add to Cart
      </button>
    </div>
  );
});

export default ProductCard;
```

**ProductSearch.jsx:**
```jsx
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import ProductCard from './ProductCard';
import { generateProducts } from './generateProducts';
import './ProductSearch.css';

function ProductSearch() {
  // Generate products once
  const products = useMemo(() => generateProducts(1000), []);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  
  // Filter states
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(1000);
  const [minRating, setMinRating] = useState(0);
  
  // Stats
  const renderCount = useRef(0);
  const searchCount = useRef(0);
  const filterTimeRef = useRef(0);
  
  // Track renders
  useEffect(() => {
    renderCount.current += 1;
  });

  // TODO: Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      // Update debouncedQuery after delay
      // Increment searchCount when query changes
    }, 300);

    return () => clearTimeout(timer);
  }, [/* dependencies? */]);

  // TODO: Get unique categories for filter
  const categories = useMemo(() => {
    // Extract unique categories from products
    // Return ['All', ...unique categories]
  }, [products]);

  // TODO: Filter products (expensive operation!)
  const filteredProducts = useMemo(() => {
    console.log('Filtering products...');
    const startTime = performance.now();
    
    let result = products;
    
    // Filter by search query
    if (debouncedQuery) {
      result = result.filter(p =>
        p.name.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(debouncedQuery.toLowerCase())
      );
    }
    
    // Filter by category
    if (selectedCategory !== 'All') {
      result = result.filter(p => p.category === selectedCategory);
    }
    
    // Filter by price range
    result = result.filter(p => p.price >= minPrice && p.price <= maxPrice);
    
    // Filter by rating
    result = result.filter(p => parseFloat(p.rating) >= minRating);
    
    const endTime = performance.now();
    filterTimeRef.current = (endTime - startTime).toFixed(2);
    
    return result;
  }, [/* dependencies? */]);

  // TODO: Memoize callback for adding to cart
  const handleAddToCart = useCallback((productId) => {
    console.log(`Added product ${productId} to cart`);
    // In real app: update cart state, call API, etc.
  }, [/* dependencies? */]);

  return (
    <div className="product-search">
      <h1>🛍️ Product Search ({products.length} products)</h1>
      
      {/* Stats Panel */}
      <div className="stats-panel">
        <div className="stat">
          <span className="stat-label">Component Renders:</span>
          <span className="stat-value">{renderCount.current}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Searches Performed:</span>
          <span className="stat-value">{searchCount.current}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Last Filter Time:</span>
          <span className="stat-value">{filterTimeRef.current}ms</span>
        </div>
      </div>

      {/* Search Input */}
      <div className="search-box">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search products..."
          className="search-input"
        />
        {searchQuery !== debouncedQuery && (
          <span className="searching-indicator">Searching...</span>
        )}
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label>Category:</label>
          <select 
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Price: ${minPrice} - ${maxPrice}</label>
          <div className="slider-group">
            <input
              type="range"
              min="0"
              max="1000"
              value={minPrice}
              onChange={(e) => setMinPrice(Number(e.target.value))}
            />
            <input
              type="range"
              min="0"
              max="1000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="filter-group">
          <label>Min Rating: {minRating}⭐</label>
          <input
            type="range"
            min="0"
            max="5"
            step="0.5"
            value={minRating}
            onChange={(e) => setMinRating(Number(e.target.value))}
          />
        </div>
      </div>

      {/* Results */}
      <div className="results-header">
        <h2>
          {filteredProducts.length} Results
          {debouncedQuery && ` for "${debouncedQuery}"`}
        </h2>
      </div>

      {/* Product Grid */}
      <div className="product-grid">
        {filteredProducts.slice(0, 50).map(product => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
          />
        ))}
      </div>

      {filteredProducts.length > 50 && (
        <p className="load-more">
          Showing 50 of {filteredProducts.length} results
        </p>
      )}

      {filteredProducts.length === 0 && (
        <p className="no-results">No products found. Try different filters!</p>
      )}
    </div>
  );
}

export default ProductSearch;
```

**ProductSearch.css:**
```css
.product-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.stats-panel {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat {
  padding: 15px 30px;
  background-color: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
}

.search-box {
  position: relative;
  margin-bottom: 30px;
}

.search-input {
  width: 100%;
  padding: 15px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #2196F3;
}

.searching-indicator {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #2196F3;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.filter-group select,
.filter-group input[type="range"] {
  width: 100%;
}

.slider-group {
  display: flex;
  gap: 10px;
}

.results-header {
  margin-bottom: 20px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.product-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  transition: box-shadow 0.3s;
}

.product-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.product-card h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.category {
  color: #2196F3;
  font-size: 14px;
  margin: 5px 0;
}

.price {
  font-size: 20px;
  font-weight: bold;
  color: #4CAF50;
  margin: 10px 0;
}

.rating {
  color: #FF9800;
  margin: 5px 0;
}

.description {
  color: #666;
  font-size: 14px;
  margin: 10px 0;
}

.product-card button {
  width: 100%;
  padding: 10px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.product-card button:hover {
  background-color: #1976D2;
}

.load-more, .no-results {
  text-align: center;
  color: #666;
  padding: 20px;
}
```

---

## 📋 Implementation Checklist

**Debouncing:**
- [ ] setTimeout in useEffect with cleanup
- [ ] Increment searchCount when query changes
- [ ] Dependencies: `[searchQuery]`

**Categories Filter:**
- [ ] useMemo to extract unique categories
- [ ] Include 'All' option
- [ ] Dependencies: `[products]`

**Filtering:**
- [ ] useMemo for filtered products
- [ ] Measure filter time with performance.now()
- [ ] Dependencies: `[products, debouncedQuery, selectedCategory, minPrice, maxPrice, minRating]`

**Callback:**
- [ ] useCallback for handleAddToCart
- [ ] Empty dependencies `[]`

---

## 💡 Complete Solutions

```jsx
// Debounce effect
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedQuery(searchQuery);
    if (searchQuery) {
      searchCount.current += 1;
    }
  }, 300);

  return () => clearTimeout(timer);
}, [searchQuery]);

// Categories
const categories = useMemo(() => {
  const unique = [...new Set(products.map(p => p.category))];
  return ['All', ...unique.sort()];
}, [products]);

// Filtered products - already provided in starter code
// Just add correct dependencies:
// [products, debouncedQuery, selectedCategory, minPrice, maxPrice, minRating]

// Callback
const handleAddToCart = useCallback((productId) => {
  console.log(`Added product ${productId} to cart`);
}, []);
```

---

## 🎨 Bonus Challenges

1. **Sort options** - Sort by price, rating, name
2. **localStorage** - Save recent searches
3. **Pagination** - Load more button instead of showing all
4. **Favorites** - Mark products as favorites with useRef
5. **Cart** - Actually implement shopping cart with state

---

## 📤 Submission

When ready, paste your code for review. I'll evaluate:
- ✅ Proper use of useRef, useMemo, useCallback
- ✅ Performance optimizations working
- ✅ No unnecessary re-renders
- ✅ Debouncing implementation
- ✅ Code quality and organization

**This project demonstrates real-world optimization patterns!** 🚀
