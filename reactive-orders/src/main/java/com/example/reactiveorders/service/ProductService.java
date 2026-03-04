package com.example.reactiveorders.service;

import com.example.reactiveorders.dto.ProductDto;
import com.example.reactiveorders.model.Product;
import com.example.reactiveorders.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    public Flux<ProductDto> getAllProducts() {
        return productRepository.findAll()
                .map(this::toDto);
    }

    public Mono<ProductDto> createProduct(ProductDto productDto) {
        return productRepository.save(toEntity(productDto))
                .map(this::toDto);
    }

    public Mono<Product> findById(String id) {
        return productRepository.findById(id);
    }

    public Mono<Product> save(Product product) {
        return productRepository.save(product);
    }

    private ProductDto toDto(Product product) {
        return ProductDto.builder()
                .id(product.getId())
                .name(product.getName())
                .price(product.getPrice())
                .stock(product.getStock())
                .build();
    }

    private Product toEntity(ProductDto dto) {
        return Product.builder()
                .name(dto.getName())
                .price(dto.getPrice())
                .stock(dto.getStock())
                .build();
    }
}
