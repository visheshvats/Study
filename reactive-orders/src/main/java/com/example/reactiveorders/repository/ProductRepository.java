package com.example.reactiveorders.repository;

import com.example.reactiveorders.model.Product;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProductRepository extends ReactiveMongoRepository<Product, String> {
    // Standard CRUD is provided out of the box.
    // ReactiveMongoRepository returns Mono/Flux types.
}
