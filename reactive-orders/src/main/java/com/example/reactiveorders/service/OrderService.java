package com.example.reactiveorders.service;

import com.example.reactiveorders.dto.OrderRequest;
import com.example.reactiveorders.dto.OrderResponse;
import com.example.reactiveorders.model.Order;
import com.example.reactiveorders.model.OrderItem;
import com.example.reactiveorders.model.OrderStatus;
import com.example.reactiveorders.model.Product;
import com.example.reactiveorders.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

        private final OrderRepository orderRepository;
        private final ProductService productService;

        public Mono<OrderResponse> createOrder(OrderRequest request) {
                log.info("Creating order for user: {}", request.getUserId());

                return Flux.fromIterable(request.getItems())
                                .flatMap(itemDto -> productService.findById(itemDto.getProductId())
                                                .switchIfEmpty(Mono.error(new RuntimeException(
                                                                "Product not found: " + itemDto.getProductId())))
                                                .flatMap(product -> {
                                                        if (product.getStock() < itemDto.getQuantity()) {
                                                                return Mono.error(new RuntimeException(
                                                                                "Insufficient stock for product: "
                                                                                                + product.getName()));
                                                        }
                                                        // Deduct stock
                                                        product.setStock(product.getStock() - itemDto.getQuantity());
                                                        return productService.save(product)
                                                                        .thenReturn(OrderItem.builder()
                                                                                        .productId(product.getId())
                                                                                        .quantity(itemDto.getQuantity())
                                                                                        .price(product.getPrice())
                                                                                        .build());
                                                }))
                                .collectList()
                                .flatMap(items -> {
                                        double totalAmount = items.stream()
                                                        .mapToDouble(item -> item.getPrice() * item.getQuantity())
                                                        .sum();

                                        Order order = Order.builder()
                                                        .userId(request.getUserId())
                                                        .items(items)
                                                        .totalAmount(totalAmount)
                                                        .status(OrderStatus.COMPLETED) // Simplifying: immediate success
                                                                                       // for now
                                                        .createdAt(Instant.now())
                                                        .build();

                                        return orderRepository.save(order);
                                })
                                .map(this::toResponse);
        }

        public Flux<OrderResponse> getOrdersByUserId(String userId) {
                return orderRepository.findByUserId(userId)
                                .map(this::toResponse);
        }

        public Mono<OrderResponse> getOrderById(String id) {
                return orderRepository.findById(id)
                                .map(this::toResponse);
        }

        private OrderResponse toResponse(Order order) {
                return OrderResponse.builder()
                                .id(order.getId())
                                .userId(order.getUserId())
                                .status(order.getStatus())
                                .totalAmount(order.getTotalAmount())
                                .createdAt(order.getCreatedAt())
                                .items(order.getItems())
                                .build();
        }
}
