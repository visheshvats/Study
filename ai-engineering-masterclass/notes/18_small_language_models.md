# Topic 18: Small Language Models (SLMs)

> **Java Analogy:** SLMs are like embedded Tomcat vs full-blown WebLogic. You don't need a 70B-parameter enterprise application server to serve a classification endpoint. A 3B model running locally is like Spring Boot's embedded server — lightweight, fast, and perfect for 80% of use cases.

---

## What This Is (Plain English)

Small Language Models (1B-7B parameters) run on laptops, phones, and edge devices — no cloud API, no internet required. They're 50-100× cheaper than frontier models and handle classification, extraction, summarization, and simple Q&A with 85-95% of the accuracy. The trade-off: they struggle with complex reasoning, long contexts, and nuanced instructions. The production strategy is to route simple queries to SLMs and complex queries to LLMs.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **SLM** | Embedded Tomcat — lightweight, fast, runs locally |
| **Frontier LLM** | WebLogic on a Kubernetes cluster — powerful, expensive, cloud-dependent |
| **Model router** | `@ConditionalOnProperty`-style routing — send to different backends based on query type |
| **Quantized SLM** | Like a compressed JAR — smaller footprint, same functionality |
| **On-device inference** | Like running `java -jar app.jar` locally — no network dependency, full data privacy |

---

## SLM vs LLM Comparison Table

| Metric | SLM (3B, INT4) | Frontier LLM (GPT-4o) |
|---|---|---|
| **Parameters** | 3 billion | ~200 billion (MoE) |
| **Memory** | 1.5-2 GB | API-only |
| **Hardware** | Laptop CPU, Raspberry Pi 5, Phone | Cloud GPU cluster |
| **Latency (TTFT)** | 30-80ms | 200-500ms |
| **Throughput** | 50-120 tok/s | 40-100 tok/s |
| **Cost per 1M tokens** | $0.00 (local) | $2.50-$10.00 |
| **Context window** | 4K-32K | 128K |
| **Classification accuracy** | 88-93% | 95-99% |
| **Complex reasoning** | 40-55% | 80-95% |
| **Data privacy** | Full (on-device) | Third-party cloud |
| **Offline capable** | Yes | No |

---

## Running SLMs from Java

### Option 1: Ollama (Recommended for Local Dev)

```bash
# Install Ollama, then pull a model
ollama pull phi3:mini     # 3.8B, ~2GB
ollama pull gemma2:2b     # 2B, ~1.4GB
ollama pull llama3.2:3b   # 3B, ~2GB
```

```java
// Spring AI with Ollama
// application.yml:
// spring.ai.ollama.chat.model: phi3:mini
// spring.ai.ollama.base-url: http://localhost:11434

@Service
public class LocalLlmService {
    private final ChatClient chatClient;

    public String classify(String text) {
        return chatClient.prompt()
            .system("Classify the text as POSITIVE, NEGATIVE, or NEUTRAL. Respond with the label only.")
            .user(text)
            .call()
            .content();
    }
}
```

### Option 2: DJL (Deep Java Library) — Pure Java Inference

```java
// Run models INSIDE the JVM — no external process needed
// Maven: ai.djl:api, ai.djl.pytorch:pytorch-engine

import ai.djl.*;
import ai.djl.inference.Predictor;
import ai.djl.translate.*;

public class DjlInference {
    public String generate(String prompt) throws Exception {
        Criteria<String, String> criteria = Criteria.builder()
            .setTypes(String.class, String.class)
            .optModelUrls("djl://ai.djl.huggingface.pytorch/microsoft/phi-2")
            .optEngine("PyTorch")
            .build();

        try (ZooModel<String, String> model = criteria.loadModel();
             Predictor<String, String> predictor = model.newPredictor()) {
            return predictor.predict(prompt);
        }
    }
}
```

### Option 3: llama.cpp via JNI

```java
// For maximum performance on CPU — llama.cpp is the fastest
// Use java-llama.cpp binding
// Maven: de.kherud:llama:3.x.x

import de.kherud.llama.*;

public class LlamaCppService {
    private final LlamaModel model;

    public LlamaCppService() {
        ModelParameters params = new ModelParameters()
            .setModelFilePath("models/phi-3-mini-q4.gguf")
            .setNGpuLayers(0);  // CPU only
        this.model = new LlamaModel(params);
    }

    public String generate(String prompt) {
        InferenceParameters inferParams = new InferenceParameters(prompt)
            .setTemperature(0.3f)
            .setNPredict(256);

        StringBuilder result = new StringBuilder();
        for (LlamaOutput output : model.generate(inferParams)) {
            result.append(output.text);
        }
        return result.toString();
    }
}
```

---

## The Model Router Architecture

```java
@Service
public class CostOptimizedRouter {
    private final ChatClient localModel;     // Phi-3 via Ollama (FREE)
    private final ChatClient cloudModel;     // GPT-4o ($2.50/1M)

    /**
     * Route 80% of queries to local SLM, 20% to cloud LLM.
     * Estimated cost savings: 80% vs all-cloud.
     */
    public String route(String query) {
        QueryComplexity complexity = classifyComplexity(query);

        return switch (complexity) {
            case SIMPLE -> localModel.prompt().user(query).call().content();
            case COMPLEX -> cloudModel.prompt().user(query).call().content();
        };
    }

    private QueryComplexity classifyComplexity(String query) {
        // Heuristic-based (fast, free)
        if (query.split("\\s+").length < 20 && !query.contains("explain") 
            && !query.contains("compare") && !query.contains("analyze")) {
            return QueryComplexity.SIMPLE;
        }
        return QueryComplexity.COMPLEX;
    }

    enum QueryComplexity { SIMPLE, COMPLEX }
}
```

---

## Key SLM Families

| Model | Params | Strength | GGUF Size (INT4) |
|---|---|---|---|
| **Phi-3-mini** | 3.8B | Reasoning, code | ~2.2 GB |
| **Gemma-2-2B** | 2B | Speed, mobile | ~1.4 GB |
| **LLaMA-3.2-3B** | 3B | General, open license | ~1.8 GB |
| **Qwen2.5-3B** | 3B | Multilingual | ~1.8 GB |
| **Mistral-7B** | 7B | Best quality at 7B | ~4.1 GB |

---

## Interview-Ready Summary

- SLMs (1-7B params) run on laptops and phones at 50-120 tokens/sec with zero API cost.
- They achieve 85-95% of frontier model accuracy on classification and extraction tasks.
- In Java: use Ollama + Spring AI (easiest), DJL (pure Java), or llama.cpp JNI (fastest).
- Production pattern: model router that sends simple queries to local SLM, complex queries to cloud LLM.
- SLMs struggle with complex reasoning, long context, and nuanced instructions.
- Cost savings of 80%+ when routing appropriately.
- Data privacy benefit: all processing stays on-device, no data leaves your infrastructure.
