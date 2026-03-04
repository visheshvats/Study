package module1;

import java.util.*;

public class CollectionsLab {

    public static void main(String[] args) {
        System.out.println("=== Module 1.1: Collections Framework Lab ===\n");

        // --- Part 1: List Performance (ArrayList vs LinkedList) ---
        runListPerformanceTest();

        // --- Part 2: The Importance of hashCode() and equals() ---
        runHashMapTest();

        // --- Part 3: Micro-Task ---
        // TODO: Your challenge is to fix the behavior in Part 2!
    }

    private static void runListPerformanceTest() {
        System.out.println("--- Part 1: ArrayList vs LinkedList ---");
        List<Integer> arrayList = new ArrayList<>();
        List<Integer> linkedList = new LinkedList<>();
        int N = 100_000;

        // Populate
        for (int i = 0; i < N; i++) {
            arrayList.add(i);
            linkedList.add(i);
        }

        // Random Access Test
        long start = System.nanoTime();
        arrayList.get(N / 2);
        long end = System.nanoTime();
        System.out.println("ArrayList get(middle): " + (end - start) + " ns");

        start = System.nanoTime();
        linkedList.get(N / 2);
        end = System.nanoTime();
        System.out.println("LinkedList get(middle): " + (end - start) + " ns");
        System.out.println("Observation: ArrayList is O(1), LinkedList is O(n) for random access.\n");
    }

    private static void runHashMapTest() {
        System.out.println("--- Part 2: HashMap Key Behavior ---");
        Map<Person, String> phoneBook = new HashMap<>();

        Person p1 = new Person("Alice", 30);
        phoneBook.put(p1, "555-1234");

        // Try to retrieve with a NEW object that has the same data
        Person p2 = new Person("Alice", 30);
        String number = phoneBook.get(p2);

        System.out.println("Putting: Alice (30) -> 555-1234");
        System.out.println("Getting with NEW Person('Alice', 30): " + number);

        if (number == null) {
            System.out.println("FAIL: Could not retrieve the number. Why?");
            System.out.println("Hint: By default, Java uses object identity (memory address) for hashCode/equals.");
        } else {
            System.out.println("SUCCESS: Retrieved " + number);
        }
    }

    // --- Micro-Task Class ---
    static class Person {
        private String name;
        private int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        // TODO: Uncomment these methods to fix the HashMap issue!
        // @Override
        // public boolean equals(Object o) {
        // if (this == o) return true;
        // if (o == null || getClass() != o.getClass()) return false;
        // Person person = (Person) o;
        // return age == person.age && Objects.equals(name, person.name);
        // }

        // @Override
        // public int hashCode() {
        // return Objects.hash(name, age);
        // }
    }
}
