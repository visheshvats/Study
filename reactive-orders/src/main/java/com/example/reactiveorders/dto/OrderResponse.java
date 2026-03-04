package com.example.reactiveorders.dto;

import com.example.reactiveorders.model.OrderStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderResponse {
    private String id;
    private String userId;
    private OrderStatus status;
    private Double totalAmount;
    private Instant createdAt;
    private List<com.example.reactiveorders.model.OrderItem> items;
}
