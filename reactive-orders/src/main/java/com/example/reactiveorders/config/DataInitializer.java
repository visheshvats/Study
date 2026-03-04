package com.example.reactiveorders.config;

import com.example.reactiveorders.model.Product;
import com.example.reactiveorders.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final ProductRepository productRepository;

    @Override
    public void run(String... args) {
        log.info("Starting data initialization...");

        productRepository.deleteAll()
                .thenMany(Flux.just(
                        Product.builder().name("Laptop").price(1200.0).stock(10).build(),
                        Product.builder().name("Phone").price(800.0).stock(20).build(),
                        Product.builder().name("Headphones").price(150.0).stock(50).build(),
                        Product.builder().name("Keyboard").price(100.0).stock(30).build()
                ))
                .flatMap(productRepository::save) // Save each product
                .subscribe(
                        savedProduct -> log.info("Saved product: {}", savedProduct.getName()), // onNext
                        err -> log.error("Error initializing data", err),                     // onError
                        () -> log.info("Data initialization complete.")                       // onComplete
                );
    }
}
