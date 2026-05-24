# Topic 17: Multi-Modal Models

> **Java Analogy:** Multi-modal models are like a `GenericConverter` that handles multiple `MediaType` inputs (`TEXT`, `IMAGE`, `AUDIO`, `VIDEO`) through a unified processing pipeline — like Spring's `HttpMessageConverter` but for AI inference.

---

## What This Is (Plain English)

Multi-modal models process images, text, audio, and video through the same Transformer architecture. An image is split into patches (like pixels grouped into tiles), each patch is converted to a vector (same dimensionality as text tokens), and then processed alongside text tokens. The model can "see" images and "read" text simultaneously, enabling tasks like: "What does this screenshot show?" or "Describe the error in this log file photo."

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Image patch** | Like splitting a `BufferedImage` into a `List<BufferedImage>` tile grid |
| **Patch → token** | `Function<BufferedImage, float[]>` — each image tile becomes a vector, same format as text tokens |
| **Visual tokens** | Image patches treated as if they were text tokens in the sequence — processed by the same attention mechanism |
| **Cross-modal attention** | Text tokens attend to image tokens and vice versa — like a `JOIN` between two tables of different data types |
| **CLIP** | A `SimilarityService` that measures how well an image matches a text description |

---

## How Images Become Tokens

```
Original Image: 1024 × 1024 pixels
         ↓ Resize
Standard Size: 224 × 224 pixels
         ↓ Split into 16×16 patches
14 × 14 = 196 patches
         ↓ Each patch → Linear projection
196 vectors of dimension 768
         ↓ Add positional embeddings
196 "visual tokens" (same format as text tokens)
         ↓ Feed into Transformer alongside text tokens
["What", "is", "in", "this", "image", "?", img_1, img_2, ..., img_196]
```

**Token cost:** A single image can consume 196-4096+ tokens of your context window. High-res modes can use 10,000+ tokens per image.

---

## Code Bridge

### Sending Images to GPT-4o (Spring AI)

```java
@Service
public class VisionService {
    private final ChatClient chatClient;

    public String analyzeImage(byte[] imageBytes, String question) {
        String base64Image = Base64.getEncoder().encodeToString(imageBytes);

        return chatClient.prompt()
            .user(u -> u
                .text(question)
                .media(MimeTypeUtils.IMAGE_PNG, 
                    new ByteArrayResource(imageBytes))
            )
            .call()
            .content();
    }

    // Analyze a URL-based image
    public String analyzeImageUrl(String imageUrl, String question) {
        return chatClient.prompt()
            .user(u -> u
                .text(question)
                .media(MimeTypeUtils.IMAGE_JPEG, 
                    URI.create(imageUrl).toURL())
            )
            .call()
            .content();
    }
}
```

### Using OpenAI Java SDK Directly

```java
public class VisionApiExample {
    public String describeImage(String imageUrl) {
        var request = ChatCompletionRequest.builder()
            .model("gpt-4o")
            .messages(List.of(
                new ChatMessage("user", List.of(
                    new TextContent("What does this image show? Be specific."),
                    new ImageContent(new ImageUrl(imageUrl, "high"))
                ))
            ))
            .maxTokens(500)
            .build();

        return openAiClient.chatCompletion(request)
            .getChoices().get(0).getMessage().getContent();
    }
}
```

### Practical Use Cases for Java Backend Engineers

```java
// 1. Document OCR + Understanding
public InvoiceData extractInvoice(byte[] invoicePdf) {
    String analysis = visionService.analyzeImage(invoicePdf,
        """
        Extract the following fields from this invoice image:
        - Invoice Number
        - Date
        - Total Amount
        - Vendor Name
        - Line Items (description, quantity, price)
        Return as JSON.
        """);
    return objectMapper.readValue(analysis, InvoiceData.class);
}

// 2. Screenshot-based Bug Reports
public BugReport analyzeBugScreenshot(byte[] screenshot, String userDescription) {
    String analysis = visionService.analyzeImage(screenshot,
        """
        A user reported a bug with this screenshot.
        User's description: "%s"
        
        Analyze the screenshot and identify:
        1. What the UI element is
        2. What appears to be wrong
        3. Possible error messages visible
        4. Suggested severity (P1-P4)
        """.formatted(userDescription));
    return parseBugReport(analysis);
}

// 3. Chart/Graph Data Extraction
public ChartData extractChartData(byte[] chartImage) {
    String data = visionService.analyzeImage(chartImage,
        "Extract the data points from this chart as a JSON array of {x, y} values.");
    return objectMapper.readValue(data, ChartData.class);
}
```

---

## Token Cost for Images

| Resolution | Patches (16×16) | Tokens Used | Cost at $2.50/1M |
|---|---|---|---|
| 224 × 224 (low) | 196 | ~200 | $0.0005 |
| 512 × 512 (medium) | 1,024 | ~1,000 | $0.0025 |
| 1024 × 1024 (high) | 4,096 | ~4,000 | $0.010 |
| High-detail tiled | N/A | ~10,000 | $0.025 |

**Always use the lowest resolution that works.** "low" detail mode is fine for screenshots and charts. "high" is needed for fine text or detailed images.

---

## Key Limitation: Visual Hallucination

```java
// The model will confidently describe things that DON'T exist in the image.
// Always verify critical visual analysis independently.

public VerifiedResult analyzeWithVerification(byte[] image, String question) {
    String llmAnalysis = visionService.analyzeImage(image, question);

    // Cross-check with dedicated OCR for text extraction
    String ocrText = tesseractService.extractText(image);

    // Cross-check with object detection model for counting
    List<DetectedObject> objects = yoloService.detect(image);

    return new VerifiedResult(llmAnalysis, ocrText, objects);
}
```

---

## Interview-Ready Summary

- Multi-modal models process images as patches → vectors → tokens, alongside text tokens.
- Images consume significant context budget: 200-10,000 tokens per image.
- Use cases for Java engineers: invoice OCR, screenshot analysis, chart extraction, document understanding.
- In Java: Spring AI `ChatClient` with `.media()` or OpenAI Java SDK with `ImageContent`.
- Always use lowest resolution that works — "low" for screenshots, "high" for fine text.
- Visual hallucination is real — always cross-check with dedicated OCR/detection tools for critical applications.
- CLIP-style models enable image↔text similarity search (like vector search but across modalities).
