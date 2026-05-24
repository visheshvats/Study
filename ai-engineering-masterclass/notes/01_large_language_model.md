# Topic 1: Large Language Model (LLM)

> **Java Analogy:** Think of an LLM as a massive `HashMap<String, ProbabilityDistribution>` that maps every possible sequence of tokens to a probability distribution over the next token — except the "map" is a neural network with billions of parameters instead of key-value pairs.

---

## What This Is (Plain English)

An LLM is a program that predicts the next word in a sequence. It was trained on trillions of words from the internet, books, and code. When you send it a prompt, it generates a response one token at a time by repeatedly asking: "Given everything so far, what's the most likely next token?"

It does **not** "understand" anything. It's a very sophisticated autocomplete engine. But the statistical patterns it learned are so rich that its outputs appear intelligent.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent You Already Know |
|---|---|
| **Model weights** | Like a serialized `model.bin` file — a frozen snapshot of learned parameters. Think of it as a massive `.ser` file. |
| **Inference** | Calling a `predict()` method. Input goes in, output comes out. Stateless per call (like a REST endpoint). |
| **Auto-regressive loop** | A `while` loop that calls `model.nextToken(context)` and appends the result to `context` until a stop condition. |
| **Context window** | Fixed-size `byte[]` buffer. If your input exceeds it, oldest data gets truncated — like a bounded `BlockingQueue`. |
| **Temperature** | A tuning knob on `Random`. Low temperature = always pick the top result (`Collections.max()`). High temperature = weighted random selection. |
| **API call to GPT/Claude** | Essentially an HTTP POST to a REST endpoint. You send JSON, you get JSON back. No different from calling any third-party service. |

---

## What You Actually Do as a Java Backend Engineer

You will almost **never** train an LLM from scratch. Your job is to:

1. **Call LLM APIs** — OpenAI, Anthropic, Google Gemini via REST/SDK
2. **Build pipelines around LLMs** — orchestration, retry logic, caching, rate limiting
3. **Manage context** — deciding what goes into the prompt (system instructions, user history, retrieved documents)
4. **Handle streaming responses** — Server-Sent Events (SSE) from the LLM API
5. **Implement guardrails** — input validation, output filtering, cost tracking

---

## Java Ecosystem & Libraries

| Library / Tool | Purpose |
|---|---|
| **LangChain4j** | The de-facto Java framework for LLM applications. Prompt templates, memory, RAG, tool calling. |
| **Spring AI** | Spring Boot integration for LLM APIs. Auto-configuration, chat clients, embedding clients. |
| **OpenAI Java SDK** | Official client for GPT models. Handles auth, streaming, function calling. |
| **Semantic Kernel (Java)** | Microsoft's orchestration framework. Plugin architecture for AI agents. |
| **DJL (Deep Java Library)** | AWS-backed library for running ML models *locally* in Java (ONNX, PyTorch, TensorFlow). |
| **Ollama + REST** | Run open-source LLMs locally. Call via `http://localhost:11434/api/generate`. |

---

## Code Bridge — Calling an LLM from Java

### Using Spring AI (Production Pattern)

```java
@Service
public class ChatService {
    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder) {
        this.chatClient = builder
            .defaultSystem("You are a helpful banking assistant.")
            .build();
    }

    public String ask(String userQuestion) {
        return chatClient.prompt()
            .user(userQuestion)
            .call()
            .content();  // Returns the generated text
    }
}
```

### Using LangChain4j

```java
ChatLanguageModel model = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("gpt-4o")
    .temperature(0.3)
    .maxTokens(1024)
    .build();

String response = model.generate("Explain microservices in one paragraph");
```

### Raw HTTP (Understanding What's Underneath)

```java
// This is what every SDK does under the hood
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.openai.com/v1/chat/completions"))
    .header("Authorization", "Bearer " + apiKey)
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("""
        {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Spring Boot?"}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        """))
    .build();

HttpResponse<String> response = httpClient.send(request, 
    HttpResponse.BodyHandlers.ofString());
```

---

## Key Parameters You Control

| Parameter | What It Does | Typical Values |
|---|---|---|
| `model` | Which LLM to use | `gpt-4o`, `claude-3.5-sonnet`, `gemini-1.5-pro` |
| `temperature` | Randomness of output | 0.0 (deterministic) → 1.0 (creative) |
| `max_tokens` | Max response length | 256–4096 |
| `top_p` | Nucleus sampling threshold | 0.9–1.0 |
| `system` message | Behavioral instructions | "You are a medical assistant..." |

---

## Production Concerns for a Java Engineer

1. **Latency:** LLM calls take 500ms–5s. Use async (`CompletableFuture`) or reactive (`Mono<String>`) patterns. Never call an LLM synchronously in a request thread.
2. **Cost:** Every token costs money. Cache responses for repeated queries (`@Cacheable` with Redis).
3. **Rate limits:** OpenAI limits to ~500 RPM on standard tiers. Implement `RateLimiter` (Resilience4j) or a token bucket.
4. **Retries:** LLM APIs return 429/500 regularly. Use exponential backoff (`@Retry`).
5. **Streaming:** For chat UIs, use SSE streaming — don't wait for the full response. Spring WebFlux handles this well.
6. **Idempotency:** LLM outputs are non-deterministic even at temperature=0 (floating-point variance). Design accordingly.

---

## Interview-Ready Summary

- An LLM is a neural network that predicts the next token given a sequence of prior tokens.
- It generates text auto-regressively in a loop: predict → append → repeat.
- The context window is a fixed-size input buffer (4K–1M tokens depending on model).
- Temperature controls randomness: 0 = deterministic, >1 = creative.
- As a Java engineer, you integrate LLMs via REST APIs or SDKs (Spring AI, LangChain4j).
- Key production concerns: latency, cost, rate limiting, streaming, and non-determinism.
