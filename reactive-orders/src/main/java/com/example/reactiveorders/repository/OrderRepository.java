package com.example.reactiveorders.repository;

import com.example.reactiveorders.model.Order;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;

@Repository
public interface OrderRepository extends ReactiveMongoRepository<Order, String> {
    // Custom finder example
    // Finds orders by userId, returning a Flux (stream) of orders
    Flux<Order> findByUserId(String userId);
}
