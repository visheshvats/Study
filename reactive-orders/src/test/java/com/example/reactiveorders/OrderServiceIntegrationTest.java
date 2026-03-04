package com.example.reactiveorders;

import com.example.reactiveorders.dto.OrderItemDto;
import com.example.reactiveorders.dto.OrderRequest;
import com.example.reactiveorders.dto.OrderResponse;
import com.example.reactiveorders.model.Product;
import com.example.reactiveorders.repository.ProductRepository;
import com.example.reactiveorders.service.OrderService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import reactor.test.StepVerifier;

import java.util.List;

@SpringBootTest
class OrderServiceIntegrationTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private ProductRepository productRepository;

    private Product savedProduct;

    @BeforeEach
    void setup() {
        // Clear and seed data for the test
        productRepository.deleteAll().block();

        Product product = Product.builder()
                .name("Integration Test Product")
                .price(100.0)
                .stock(10)
                .build();

        savedProduct = productRepository.save(product).block();
    }

    @Test
    void shouldCreateOrderAndDeductStock() {
        // Arrange
        OrderRequest request = OrderRequest.builder()
                .userId("user-123")
                .items(List.of(
                        OrderItemDto.builder()
                                .productId(savedProduct.getId())
                                .quantity(2)
                                .build()))
                .build();

        // Act & Assert
        StepVerifier.create(orderService.createOrder(request))
                .assertNext(response -> {
                    assert response.getUserId().equals("user-123");
                    assert response.getTotalAmount() == 200.0;
                    assert response.getItems().size() == 1;
                })
                .verifyComplete();

        // Verify Side Effect: Stock Deduction
        StepVerifier.create(productRepository.findById(savedProduct.getId()))
                .assertNext(product -> {
                    assert product.getStock() == 8; // 10 - 2
                })
                .verifyComplete();
    }
}
