# MODULE 0: Foundations of AI and LLMs — Complete Notes

> **For:** Software engineers with Java/Spring Boot background, new to AI.  
> **Analogy style:** We'll map AI concepts to things you already know.

---

# LESSON 0.1: The AI Family Tree

## What is AI (Artificial Intelligence)?

**Simple:** Making computers do things that normally require human intelligence.

**Technical:** A branch of computer science that creates systems capable of performing tasks
like understanding language, recognizing images, making decisions, and generating content.

**Java Analogy:** Think of AI as the broadest `interface` — it defines the *contract* for
intelligent behavior. Everything else *implements* this interface.

```
┌─────────────────────────────────────────────────────┐
│                 ARTIFICIAL INTELLIGENCE              │
│    (Any technique that enables machines to mimic     │
│     human intelligence)                              │
│                                                      │
│   ┌─────────────────────────────────────────────┐   │
│   │          MACHINE LEARNING                    │   │
│   │   (Learning from data, not explicit rules)   │   │
│   │                                              │   │
│   │   ┌─────────────────────────────────────┐   │   │
│   │   │       DEEP LEARNING                  │   │   │
│   │   │  (Neural networks with many layers)  │   │   │
│   │   │                                      │   │   │
│   │   │   ┌─────────────────────────────┐   │   │   │
│   │   │   │    GENERATIVE AI             │   │   │   │
│   │   │   │ (Creates new content)        │   │   │   │
│   │   │   │                              │   │   │   │
│   │   │   │   ┌─────────────────────┐   │   │   │   │
│   │   │   │   │       LLMs           │   │   │   │   │
│   │   │   │   │ (Language models)    │   │   │   │   │
│   │   │   │   └─────────────────────┘   │   │   │   │
│   │   │   └─────────────────────────────┘   │   │   │
│   │   └─────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## What is Machine Learning (ML)?

**Simple:** Instead of writing `if-else` rules, you give the computer data and it *learns*
the rules itself.

**Java Analogy:**
- **Traditional programming** = You write a `RuleEngine` class with explicit business logic.
- **Machine learning** = You give the system input/output examples, and it auto-generates
  the rules.

```
Traditional Programming:
  DATA + RULES ──→ ANSWERS

Machine Learning:
  DATA + ANSWERS ──→ RULES (model)
```

### Types of ML

| Type | What it does | Example |
|------|-------------|---------|
| **Supervised** | Learns from labeled data | Spam detection (email → spam/not spam) |
| **Unsupervised** | Finds patterns in unlabeled data | Customer segmentation |
| **Reinforcement** | Learns by trial and error (rewards) | Game AI, robotics |

---

## What is Deep Learning?

**Simple:** ML using **neural networks** with many layers (hence "deep").

**Why it matters:** Traditional ML struggled with unstructured data (images, text, audio).
Deep learning handles it beautifully.

```
Input Layer      Hidden Layers (the "deep" part)     Output Layer
    ●─────────────●──────●──────●──────────────────── ●
    ●─────────────●──────●──────●──────────────────── ●
    ●─────────────●──────●──────●
    ●─────────────●──────●──────●

Each ● = a "neuron" (a small math function)
Each ─ = a "weight" (a number that gets adjusted during training)
```

**Java Analogy:** Imagine a chain of `Filter` classes in a Spring pipeline. Each filter
transforms the data slightly. Deep learning is like having 100+ filters that *automatically
learn* what transformations to apply.

---

## What is NLP (Natural Language Processing)?

**Simple:** Teaching computers to understand, interpret, and generate human language.

**Examples:**
- Spell check → NLP
- Google Translate → NLP
- ChatGPT → NLP + Deep Learning + Generative AI

**Evolution:**

```
Rule-based NLP (1960s)     →  "if word == 'good' then sentiment = positive"
Statistical NLP (2000s)    →  Count word frequencies, use probability
Deep Learning NLP (2018+)  →  Transformers, BERT, GPT
```

---

## What is Generative AI?

**Simple:** AI that **creates new content** — text, images, code, music, video.

**Key difference:**
- Traditional AI: **classifies** or **predicts** (is this email spam? yes/no)
- Generative AI: **creates** (write me an email, generate an image)

**Examples:**

| Model | Creates |
|-------|---------|
| GPT-4 | Text, code |
| DALL·E | Images |
| Suno | Music |
| Sora | Video |

---

## What is an LLM (Large Language Model)?

**Simple:** A very large neural network trained on massive amounts of text that can
understand and generate human language.

**Breaking it down:**
- **Large** → Billions of parameters (GPT-4 has ~1.7 trillion)
- **Language** → Specializes in human language
- **Model** → A mathematical function that takes input and produces output

**How it works at the simplest level:**

```
Input:  "The capital of France is ___"
                    │
                    ▼
            ┌──────────────┐
            │     LLM      │
            │ (predicts the │
            │  next token)  │
            └──────────────┘
                    │
                    ▼
Output: "Paris"
```

> **Key insight:** LLMs are fundamentally **next-token predictors**. They predict the most
> likely next word (token) given the previous words. That's it. The magic is that this
> simple objective, at massive scale, produces remarkably intelligent behavior.

**Java Analogy:** Think of an LLM as a `Function<String, String>` — you give it text in,
you get text out. But internally, it's a neural network with billions of parameters
that were trained on the entire internet.

### Popular LLMs

| Model | Company | Parameters | Open Source? |
|-------|---------|-----------|-------------|
| GPT-4o | OpenAI | ~1.7T | No |
| Claude 3.5 | Anthropic | Unknown | No |
| Gemini | Google | Unknown | No |
| Llama 3 | Meta | 8B–405B | Yes |
| Mistral | Mistral AI | 7B–8x22B | Yes |

---

# LESSON 0.2: Core Concepts You MUST Know

## 1. Tokens

**Simple:** Tokens are the **smallest units** that an LLM works with. They are NOT words —
they're pieces of words.

```
"Hello, how are you?"

Tokens: ["Hello", ",", " how", " are", " you", "?"]
         ──1───  ─2─  ──3──  ──4──  ──5──  ─6─

That's 6 tokens for 4 words.
```

**Why it matters:**
- LLMs have **token limits** (not word limits)
- You **pay per token** when using APIs
- GPT-4o: ~$2.50 per 1M input tokens

**Rule of thumb:** 1 token ≈ ¾ of a word (in English). So 100 tokens ≈ 75 words.

**Java Analogy:** Think of tokenization like `String.split()` but much smarter. Instead of
splitting on spaces, the LLM uses **BPE (Byte Pair Encoding)** which splits based on
frequency patterns in training data.

```
"unhappiness" → ["un", "happiness"]    // BPE splits into common sub-words
"Kafka"       → ["Kaf", "ka"]          // Less common words get split more
"the"         → ["the"]                // Common words stay whole
```

---

## 2. Embeddings

**Simple:** Embeddings convert text into **numbers** (vectors) that capture **meaning**.

**Why?** Computers can't understand "King" and "Queen", but they CAN compare
`[0.2, 0.8, 0.1, ...]` and `[0.25, 0.78, 0.15, ...]`.

```
Words in human space:         Words in vector space (simplified to 2D):

  King                              ● King (0.9, 0.9)
  Queen                             ● Queen (0.85, 0.88)
  Man                               ● Man (0.9, 0.1)
  Woman                             ● Woman (0.85, 0.12)
  Apple                             ● Apple (0.1, 0.5)

The magical property:
  King - Man + Woman ≈ Queen     (vector arithmetic!)
```

**Real embeddings:** Not 2D, but 1536 dimensions (OpenAI) or 768 dimensions (BERT).

**Java Analogy:** Think of it as converting objects to a common `Comparable` format.
You can't directly compare a `Customer` and a `Product`, but if you convert both to
a numeric vector, you can compute their "similarity."

---

## 3. Context Window

**Simple:** The **maximum amount of text** an LLM can see at once (input + output combined).

```
┌──────────────────────────────────────────┐
│           CONTEXT WINDOW (128K)          │
│                                          │
│  ┌────────────┐  ┌───────────────────┐  │
│  │   INPUT     │  │     OUTPUT        │  │
│  │  (prompt +  │  │  (LLM response)   │  │
│  │   context)  │  │                   │  │
│  └────────────┘  └───────────────────┘  │
│                                          │
│  ← These SHARE the same window →        │
└──────────────────────────────────────────┘
```

| Model | Context Window |
|-------|---------------|
| GPT-4o | 128K tokens |
| Claude 3.5 | 200K tokens |
| Gemini 1.5 Pro | 1M tokens |
| Llama 3 | 8K–128K tokens |

**Java Analogy:** Context window is like JVM heap size (`-Xmx`). If your data exceeds it,
you get an error (or in LLM terms, the model silently forgets older parts).

**Why it matters for Agents/RAG:** You can't feed an entire database to an LLM. That's why
we need RAG — to fetch only the relevant pieces that fit in the context window.

---

## 4. Temperature

**Simple:** Controls **randomness** of the LLM output. It's a number between 0 and 2.

```
Temperature = 0.0  →  Deterministic, always picks the most likely token
                       "The sky is BLUE" (always blue)

Temperature = 0.7  →  Balanced creativity
                       "The sky is BLUE/AZURE/CLEAR" (some variety)

Temperature = 1.5  →  Very creative/random
                       "The sky is WHISPERING" (unexpected, poetic)
```

**When to use what:**

| Temperature | Use Case |
|------------|----------|
| 0.0 | Code generation, factual Q&A, data extraction |
| 0.3–0.7 | General conversation, content writing |
| 0.8–1.2 | Creative writing, brainstorming |

**Java Analogy:** `temperature = 0` is like using `Collections.max()` — always picks the
top result. `temperature = 1.0` is like weighted `Random` selection.

---

## 5. Hallucination

**Simple:** When an LLM **confidently generates false information**.

**Example:**
```
You: "Who wrote the book 'The Neural Networks of Neptune'?"
LLM: "This groundbreaking book was written by Dr. Sarah Mitchell in 2019..."

Reality: This book doesn't exist. The LLM made it up.
```

**Why it happens:**
1. LLMs are **pattern matchers**, not knowledge databases
2. They predict what text *should look like*, not what's *true*
3. They never say "I don't know" naturally — they're trained to always produce output

**How to mitigate:**
- Use **RAG** (ground the LLM in real documents)
- Use **lower temperature** (less creativity = fewer inventions)
- Ask the LLM to **cite sources**
- Use **guardrails** and validation

**Java Analogy:** Hallucination is like an `auto-complete` in your IDE suggesting a method
that doesn't exist. It *looks right* syntactically but is actually wrong.

---

## 6. Fine-Tuning vs Prompt Engineering

These are two ways to **customize LLM behavior**. Understanding the difference is critical.

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMIZING AN LLM                       │
│                                                              │
│  ┌───────────────────────┐  ┌────────────────────────────┐  │
│  │  PROMPT ENGINEERING    │  │      FINE-TUNING           │  │
│  │                        │  │                            │  │
│  │  • Change the INPUT    │  │  • Change the MODEL        │  │
│  │  • No training needed  │  │  • Requires training data  │  │
│  │  • Instant             │  │  • Takes hours/days        │  │
│  │  • Cheap               │  │  • Expensive               │  │
│  │  • Flexible            │  │  • Permanent change        │  │
│  │                        │  │                            │  │
│  │  "Please respond in    │  │  Train GPT on 10K medical  │  │
│  │   JSON format..."      │  │  records so it speaks      │  │
│  │                        │  │  like a doctor natively    │  │
│  └───────────────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

| Aspect | Prompt Engineering | Fine-Tuning |
|--------|-------------------|-------------|
| **What changes** | Input prompt | Model weights |
| **Cost** | API call cost only | $$ for training compute |
| **Time** | Instant | Hours to days |
| **When to use** | Start here ALWAYS | When prompts aren't enough |
| **Skill level** | Beginner | Advanced |
| **Reversible** | Yes | No (you get a new model) |

**Java Analogy:**
- **Prompt Engineering** = Changing the `@RequestBody` you send to a REST API
- **Fine-Tuning** = Recompiling the microservice with new training data baked in

> **Rule of thumb:** Always try prompt engineering first. Only fine-tune when you have
> a specific, repeated pattern that prompts can't handle efficiently.

---

# LESSON 0.3: Transformer Architecture & Attention Mechanism

## Why Transformers?

**Before Transformers (pre-2017):** We used RNNs (Recurrent Neural Networks) and LSTMs
for language tasks. They processed words **one at a time, sequentially**.

**Problem:** Like reading a book one letter at a time — slow and you forget the beginning
by the time you reach the end.

**Transformers (2017):** Introduced in the paper *"Attention Is All You Need"*. They
process **all words simultaneously** using **attention**.

```
RNN (Sequential):                    Transformer (Parallel):
  "I" → "love" → "coding" → ...       "I", "love", "coding" → all at once!
  s₁ →   s₂   →    s₃                 Processes entire sentence in parallel

  Slow, sequential                     Fast, parallel, better memory
```

---

## Transformer Architecture (Simplified)

```
                    ┌──────────────────────┐
                    │      OUTPUT           │
                    │  "Paris"              │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Linear + Softmax   │
                    │  (probability over   │
                    │   all tokens)         │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
              ×N   │   DECODER BLOCK       │
              │    │  ┌──────────────────┐ │
              │    │  │ Feed Forward NN   │ │
              │    │  └────────┬─────────┘ │
              │    │  ┌────────▼─────────┐ │
              │    │  │ Cross-Attention   │ │  ← Looks at encoder output
              │    │  └────────┬─────────┘ │
              │    │  ┌────────▼─────────┐ │
              │    │  │ Self-Attention    │ │  ← Looks at previous outputs
              │    │  └──────────────────┘ │
              │    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
              ×N   │   ENCODER BLOCK       │
              │    │  ┌──────────────────┐ │
              │    │  │ Feed Forward NN   │ │
              │    │  └────────┬─────────┘ │
              │    │  ┌────────▼─────────┐ │
              │    │  │ Self-Attention    │ │  ← Each word attends to
              │    │  │                   │ │    every other word
              │    │  └──────────────────┘ │
              │    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Positional Encoding   │
                    │ + Token Embeddings    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │       INPUT           │
                    │ "Capital of France?"  │
                    └──────────────────────┘
```

**Note:** GPT (the "G" in ChatGPT) uses only the **Decoder** part. BERT uses only the
**Encoder** part. The original Transformer uses both.

---

## Attention Mechanism — The Core Idea

**Simple Analogy:**

Imagine you're reading this sentence: *"The cat sat on the mat because **it** was tired."*

What does "it" refer to? The **cat**, not the mat. You know this because your brain
**attends** to (focuses on) the relevant words.

That's exactly what attention does — for each word, it decides **how much to focus on
every other word**.

```
Attention for the word "it":

  The   cat   sat   on   the   mat   because   it   was   tired
  0.05  0.60  0.05  0.01  0.02  0.10   0.02   1.0  0.05   0.10
        ^^^^                                         
   "it" pays the MOST attention to "cat"
```

---

## Self-Attention (Step by Step)

For each word, self-attention computes three vectors:
- **Q (Query):** "What am I looking for?"
- **K (Key):** "What do I contain?"  
- **V (Value):** "What information do I provide?"

```
Step 1: Create Q, K, V for each word

  "I love coding"
   │    │     │
   ▼    ▼     ▼
  Q₁   Q₂   Q₃   ← What am I looking for?
  K₁   K₂   K₃   ← What do I contain?
  V₁   V₂   V₃   ← What info do I provide?


Step 2: Compute attention scores (Q × K^T)

       K₁    K₂    K₃
  Q₁ [ 0.8   0.1   0.1 ]   ← "I" mostly attends to itself
  Q₂ [ 0.3   0.5   0.2 ]   ← "love" attends to itself and "I"  
  Q₃ [ 0.2   0.3   0.5 ]   ← "coding" attends to itself and "love"


Step 3: Multiply scores × Values to get output

  Output₁ = 0.8×V₁ + 0.1×V₂ + 0.1×V₃
  Output₂ = 0.3×V₁ + 0.5×V₂ + 0.2×V₃
  Output₃ = 0.2×V₁ + 0.3×V₂ + 0.5×V₃
```

**Java Analogy:** Self-attention is like a `JOIN` in SQL. Each word "joins" with every
other word, and the attention score is the "join weight" that determines which
connections matter most.

---

## Multi-Head Attention

Instead of one attention mechanism, Transformers use **multiple attention heads** in
parallel. Each head learns to focus on **different types of relationships**.

```
Head 1: Focuses on syntactic relationships  (subject-verb)
Head 2: Focuses on semantic relationships   (meaning similarity)
Head 3: Focuses on positional relationships (nearby words)
...
Head 12: Focuses on some other pattern

All heads run in PARALLEL → concatenate results → linear projection
```

**Java Analogy:** Multi-head attention is like having multiple `Comparator` implementations.
Each one sorts by a different criteria, and you combine the results.

---

# LESSON 0.4: Code Examples

See the `code/` directory for runnable examples:

1. **`01_call_llm_api.py`** — Call OpenAI API, understand request/response
2. **`02_basic_prompts.py`** — Different prompt styles and temperature effects
3. **`03_token_counting.py`** — Count tokens, estimate costs
4. **`04_chatbot.py`** — Simple chatbot with conversation history

---

# LESSON 0.5: Exercises

## Exercise 1: Concept Check
1. In your own words, explain why an LLM sometimes "hallucinates."
2. If GPT-4o has a 128K token context window, approximately how many words can it process?
3. What temperature would you use for generating unit tests? Why?

## Exercise 2: Token Estimation
Given this text: `"Spring Boot simplifies Java web application development"`
1. Estimate how many tokens this is (without running code)
2. Run the token counting script to verify

## Exercise 3: API Exploration
1. Call the OpenAI API with temperature=0 three times with the same prompt. Are results identical?
2. Repeat with temperature=1.0. How do results differ?
3. Try temperature=2.0. What happens?

## Exercise 4: Build Something
Modify the chatbot to:
1. Have a system prompt that makes it behave as a Java Spring Boot expert
2. Keep conversation history (use a list)
3. Add a `/clear` command to reset history

---

# LESSON 0.6: Interview Questions & Answers

## Q1: What is the difference between AI, ML, and Deep Learning?

**Answer:** AI is the broadest concept — any system that mimics human intelligence. ML is a
subset of AI where systems learn from data instead of explicit rules. Deep Learning is a
subset of ML that uses multi-layered neural networks and excels at unstructured data
(text, images, audio). All LLMs are Deep Learning models, which are ML systems,
which are AI systems.

## Q2: How does an LLM generate text?

**Answer:** An LLM generates text by **predicting one token at a time**. Given an input
sequence, it calculates the probability distribution over all possible next tokens, picks
one (influenced by temperature), appends it, and repeats until it reaches a stop condition.
This is called **autoregressive generation**.

## Q3: What is the attention mechanism and why was it a breakthrough?

**Answer:** Attention allows the model to focus on relevant parts of the input when
generating each output token. Before attention, RNNs processed sequences sequentially and
struggled with long-range dependencies. Attention enables **parallel processing** and
direct connections between any two positions, regardless of distance. The paper
"Attention Is All You Need" (2017) showed that attention alone (without RNNs) could
achieve state-of-the-art results.

## Q4: Explain the difference between fine-tuning and prompt engineering.

**Answer:** Prompt engineering changes the **input** to guide the model's behavior without
modifying the model itself — it's cheap, fast, and reversible. Fine-tuning changes the
**model weights** by training on domain-specific data — it's expensive, slow, but produces
a permanently customized model. Always start with prompt engineering. Fine-tune only when
you have thousands of domain-specific examples and prompts can't achieve the desired
quality.

## Q5: What are tokens and why do they matter?

**Answer:** Tokens are the smallest units of text an LLM processes, typically sub-word
chunks. They matter because: (1) LLMs have maximum token limits (context window), (2) API
costs are per-token, (3) different languages tokenize differently (Chinese uses more tokens
per character than English), (4) token boundaries can affect output quality.

## Q6: What is hallucination and how do you prevent it in production?

**Answer:** Hallucination is when an LLM generates confident but factually incorrect
information. Prevention strategies: (1) Use RAG to ground responses in real documents,
(2) Lower temperature for factual tasks, (3) Ask the model to say "I don't know" when
uncertain, (4) Implement output validation and fact-checking pipelines, (5) Use structured
output formats to constrain responses.

## Q7: What is the context window and how does it affect system design?

**Answer:** The context window is the maximum number of tokens (input + output) the model
can process at once. It affects system design because: (1) You can't feed unlimited data
to an LLM, necessitating chunking and selection strategies, (2) RAG exists specifically
because context windows are limited, (3) Conversation history must be managed to stay
within limits, (4) Longer context windows are more expensive to use.

---

# Real-World Production Use Cases

| Use Case | How LLMs are Used | Company Example |
|----------|------------------|-----------------|
| Customer Support | Chatbots that understand context | Zendesk, Intercom |
| Code Generation | AI pair programmers | GitHub Copilot, Cursor |
| Document Analysis | Extract info from contracts, reports | Legal tech, Finance |
| Search | Semantic search (not just keyword) | Google, Elasticsearch |
| Content Creation | Marketing copy, emails, summaries | Jasper, Copy.ai |
| Data Extraction | Parse unstructured data into structured | Healthcare, Insurance |

---

# Common Mistakes (Beginners)

| Mistake | Why it's wrong | Correct approach |
|---------|---------------|-----------------|
| Treating LLM as a database | LLMs don't "know" facts, they predict patterns | Use RAG for factual queries |
| Ignoring token costs | Long prompts = expensive at scale | Optimize prompts, cache responses |
| Temperature always at default | Different tasks need different creativity | Tune per use case |
| No error handling for API calls | APIs can fail, rate limit, timeout | Implement retries, fallbacks |
| Trusting LLM output blindly | Hallucinations are common | Always validate critical outputs |
| Jumping to fine-tuning | Expensive and usually unnecessary | Try prompt engineering first |

---

# Best Practices

1. **Start simple** — Use prompt engineering before anything complex
2. **Validate outputs** — Never trust LLM output for critical decisions without verification
3. **Monitor costs** — Track token usage; set billing alerts
4. **Use streaming** — For better UX, stream responses token-by-token
5. **Handle failures** — Implement retry logic with exponential backoff
6. **Version your prompts** — Treat prompts like code; store in version control
7. **Test systematically** — Create eval datasets to measure prompt quality
8. **Stay updated** — The field moves fast; new models drop monthly

---

**Next Module:** [Module 1 — Prompt Engineering →](../module-1-prompt-engineering/)

Say **NEXT** to continue.
