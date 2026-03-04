# Coding Prompts

## 1. Implement LRU Cache.
Using `LinkedHashMap`.

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCache(int capacity) {
        // true for access-order (LRU), false for insertion-order
        super(capacity, 0.75f, true); 
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity; // Remove if size exceeds limit
    }
    
    public static void main(String[] args) {
        LRUCache<Integer, String> cache = new LRUCache<>(2);
        cache.put(1, "A");
        cache.put(2, "B");
        cache.get(1); // Access 1, making 2 the LRU
        cache.put(3, "C"); // Should evict 2
        System.out.println(cache); // {1=A, 3=C}
    }
}
```

## 2. Group anagrams.

```java
public List<List<String>> groupAnagrams(String[] strs) {
    if (strs == null || strs.length == 0) return new ArrayList<>();
    
    Map<String, List<String>> map = new HashMap<>();
    
    for (String s : strs) {
        char[] ca = s.toCharArray();
        Arrays.sort(ca); 
        String key = String.valueOf(ca); // Sorted string as key
        
        map.putIfAbsent(key, new ArrayList<>());
        map.get(key).add(s);
    }
    
    return new ArrayList<>(map.values());
}
```

## 3. Top K frequent elements.
Using PriorityQueue (Min Heap).

```java
public int[] topKFrequent(int[] nums, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    for (int n : nums) count.put(n, count.getOrDefault(n, 0) + 1);

    // Min Heap keeps smallest counts at top
    PriorityQueue<Integer> heap = new PriorityQueue<>(
        (a, b) -> count.get(a) - count.get(b)
    );

    for (int n : count.keySet()) {
        heap.add(n);
        if (heap.size() > k) heap.poll(); // Remove least frequent
    }

    // Convert to array
    int[] top = new int[k];
    for(int i = 0; i < k; i++) top[i] = heap.poll();
    return top;
}
```

## 4. Detect cycle in linked list.
Tortoise and Hare algorithm.

```java
public boolean hasCycle(ListNode head) {
    if (head == null) return false;
    ListNode slow = head;
    ListNode fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;       // 1 step
        fast = fast.next.next;  // 2 steps
        
        if (slow == fast) return true; // Collision
    }
    return false;
}
```

## 5. Producer-consumer using blocking queue.

```java
import java.util.concurrent.*;

public class ProducerConsumer {
    public static void main(String[] args) {
        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(10);

        // Producer
        new Thread(() -> {
            try {
                while(true) {
                    queue.put(1); // Blocks if full
                    System.out.println("Produced");
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        }).start();

        // Consumer
        new Thread(() -> {
            try {
                while(true) {
                    queue.take(); // Blocks if empty
                    System.out.println("Consumed");
                    Thread.sleep(1000);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        }).start();
    }
}
```

## 6. Implement a thread-safe counter with high throughput.
Use `AtomicInteger` or `LongAdder`.

```java
import java.util.concurrent.atomic.LongAdder;

public class Counter {
    // LongAdder is faster than AtomicLong under high contention
    // because it stripes writes across variables to avoid cache invalidation.
    private final LongAdder count = new LongAdder();

    public void increment() {
        count.increment();
    }

    public long get() {
        return count.sum();
    }
}
```

## 7. Parse logs and compute per-user metrics efficiently.

Concept: Read chunks, process map-reduce style.

```java
public Map<String, Long> processLogs(List<String> logs) {
    return logs.stream()
        .parallel() // Useful if list is huge
        .map(log -> parseUser(log)) // Extract UserID
        .collect(Collectors.groupingBy(
            user -> user, 
            Collectors.counting()
        ));
}
```
