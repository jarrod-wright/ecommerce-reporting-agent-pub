### **Architectural Design Document: The Agnostic LLM Service Layer (v2.0)**

**Document ID:** ADD-LLM-SERVICE-V2.0
**Project:** E-commerce Performance Report Agent
**Status:** FINAL

---

### **Part 1: The Human-Centric Blueprint**

This document details the architecture for a provider-agnostic, enterprise-grade LLM service layer. It is structured to provide a clear, comprehensive overview for all human stakeholders, from the strategic "why" to the technical "how."

#### **1.1 The Executive Lens: Building a Strategic, Future-Proof Asset**

*   **The Strategic Imperative:** The core mission of this agency is to sell **"Productized Trust"** and deliver high-value, risk-mitigated AI solutions. Tightly coupling our core product to a single Large Language Model (LLM) provider is a critical strategic risk. It introduces vendor lock-in, stifles innovation, and prevents us from optimizing for the best cost-performance ratio as the market evolves.

*   **The Solution - An "Interchangeable Engine":** We are architecting our "AI Software Factory" with an interchangeable engine. This document outlines the design for a **provider-agnostic, "pluggable" LLM service layer.** This is not a technical feature; it is a core business capability that allows us to treat LLM providers as commodities, not dependencies.

*   **The Defensible Business Value:** This architecture is a key component of our defensible moat and directly translates into tangible business value:
    *   **Competitive Agility:** We can onboard and offer a new, state-of-the-art model (e.g., a future GPT-5 or a specialized open-source model) in days, not months, keeping our service offerings on the absolute cutting edge.
    *   **Margin Optimization:** We can dynamically select the most cost-effective model for a given task, allowing us to protect our margins and offer more competitive pricing to clients.
    *   **Client Choice & Trust:** We can offer clients a choice of best-in-class models (Anthropic for safety, Google for integration, etc.), positioning us as an expert, unbiased advisor, not a single-product reseller.

---

#### **1.2 The Team Lead Lens: Architecting for Scalability & Maintainability**

*   **The Architectural Mandate:** We will implement the **"Dependency Inversion Principle"** using a classic **"Interface and Factory"** software design pattern. This is a non-negotiable standard that ensures our high-level business logic is cleanly decoupled from low-level implementation details.

*   **The System Components (Visualized):**
    

*   **The Breakdown:**
    1.  **The Interface (The "Standard Socket"):** We will define a Python `abstract base class` (ABC) named `LLMClient`. This class acts as a formal "contract." It dictates that any class wanting to be an "LLM Client" in our system *must* provide a specific method with a specific signature (e.g., `generate_structured_output`).
    2.  **The Concrete Implementations (The "Adapters"):** For each LLM provider we support, we will create a separate, dedicated class (e.g., `AnthropicClient`, `GoogleAIClient`) that inherits from our `LLMClient` interface. Each of these classes is a self-contained module that handles all the provider-specific logic (authentication, library calls, error handling).
    3.  **The Factory (The "Power Strip"):** We will create a simple factory function (`get_llm_client`). Its only job is to look at a configuration (e.g., a string that says "ANTHROPIC") and return an instantiated object of the correct concrete class (`AnthropicClient()`).

*   **The Resulting Workflow:** Our core application logic (the LangGraph nodes) will be completely "ignorant" of which specific LLM provider is being used. A node will simply ask the factory for "an LLM Client that adheres to the standard contract." This makes our graph logic incredibly clean, stable, and easy to test, as it never needs to change, even when we add or remove LLM providers.

---

#### **1.3 The Engineer Lens: The "Golden Standard" Implementation Plan**

*   **Core Technology:** Python 3.11+, `abc` module for the interface, `langchain_anthropic` and `langchain_google_genai` for the concrete implementations, and `Pydantic` for the structured data schemas.

*   **File & Directory Structure:**
    *   **The Contract:** `agent/clients/llm_interface.py` - Will contain the `LLMClient(ABC)` class definition.
    *   **The Adapters:**
        *   `agent/clients/anthropic_client.py` - Will contain the `AnthropicClient(LLMClient)` class.
        *   `agent/clients/google_client.py` - Will contain the `GoogleAIClient(LLMClient)` class.
    *   **The Factory:** `agent/clients/factory.py` - Will contain the `get_llm_client()` function.
    *   **The "Package" File:** `agent/clients/__init__.py` - Will make these components easily importable throughout the application.

*   **Test-Driven Development (TDD) Plan:** The implementation will follow our mandated TDD workflow.
    1.  **Cycle 1 (The Interface & First Adapter):** We will first write a failing test that asserts the existence of the `LLMClient` interface and the `AnthropicClient` subclass. We will then write the code to make this test pass. This validates our core abstraction and our first concrete implementation simultaneously.
    2.  **Cycle 2 (The Second Adapter):** We will then write a failing test for the `GoogleAIClient`. Because our interface is already defined, this cycle will be significantly faster, demonstrating the extensibility of our architecture.
    3.  **Testing Strategy:** All tests for the concrete clients will be 100% hermetic. We will use `pytest-mock` to patch the actual LangChain library calls (e.g., `patch("langchain_anthropic.ChatAnthropic")`). Our tests will verify that our client classes correctly handle authentication and call the underlying libraries with the expected arguments, without ever making a real network call.
    
---

### **Part 2: The Machine-Readable Mandate (For Claude Code)**

**START OF MACHINE MANDATE**

**DOCUMENT:** ARCHITECTURAL DESIGN DOCUMENT - ADD-LLM-SERVICE-V2.0

**SUBJECT:** The Agnostic LLM Service Layer

**PRIMARY DIRECTIVE:** Your primary architectural goal for all LLM interaction is to build a **provider-agnostic service layer**. You MUST adhere to the "Interface and Factory" pattern described herein. The core business logic MUST be completely decoupled from any specific LLM provider's implementation.

**MANDATORY COMPONENTS & FILE STRUCTURE:**

1.  **The Interface (The "Contract"):**
    *   **File:** `agent/clients/llm_interface.py`
    *   **Content:** An abstract base class named `LLMClient` defined with `from abc import ABC, abstractmethod`. It must also import `from pydantic import BaseModel`.
    *   **Contract:** It MUST define one abstract method: `generate_structured_output(self, prompt: str, output_schema: type[BaseModel]) -> BaseModel`. Note the type hint for `output_schema` is `type[BaseModel]`, as we are passing the class itself.

2.  **Concrete Implementations (The "Adapters"):**
    *   **File (Anthropic):** `agent/clients/anthropic_client.py`
        *   **Content:** A class named `AnthropicClient` that inherits from `LLMClient`.
        *   **Implementation:**
            *   Its `__init__` method must import `os`, retrieve `ANTHROPIC_API_KEY` from environment variables, and instantiate `ChatAnthropic` from `langchain_anthropic`, storing it as a private instance variable. It must raise a `ValueError` if the API key is not found.
            *   It must implement the `generate_structured_output` method, which takes a `prompt` and `output_schema`. It MUST use the `with_structured_output` pattern on its internal `ChatAnthropic` instance, passing the `output_schema`.
    *   **File (Google):** `agent/clients/google_client.py`
        *   **Content:** A class named `GoogleAIClient` that inherits from `LLMClient`.
        *   **Implementation:**
            *   Its `__init__` method must import `os`, retrieve `GOOGLE_API_KEY` from environment variables, and instantiate `ChatGoogleGenerativeAI` from `langchain_google_genai`, storing it as a private instance variable. It must raise a `ValueError` if the API key is not found.
            *   It must implement the `generate_structured_output` method, which takes a `prompt` and `output_schema`. It MUST use the `with_structured_output` pattern on its internal `ChatGoogleGenerativeAI` instance, passing the `output_schema`.

3.  **The Factory (The "Selector"):**
    *   **File:** `agent/clients/factory.py`
    *   **Content:** A function `get_llm_client(provider: str) -> LLMClient`.
    *   **Logic:** It must take a string (`"ANTHROPIC"` or `"GOOGLE"`) as input and return an instantiated `AnthropicClient()` or `GoogleAIClient()` respectively. It should raise a `ValueError` for any unknown provider string.

4.  **The Package Initializer:**
    *   **File:** `agent/clients/__init__.py`
    *   **Content:** This file must expose the key components for easy import. It should contain:
        ```python
        from .llm_interface import LLMClient
        from .anthropic_client import AnthropicClient
        from .google_client import GoogleAIClient
        from .factory import get_llm_client
        ```

**TESTING PROTOCOL (MANDATORY):**

*   Each concrete client (`AnthropicClient`, `GoogleAIClient`) MUST have its own dedicated test file in `tests/clients/`.
*   Tests for each client MUST verify that it correctly inherits from the `LLMClient` interface.
*   Tests MUST use `pytest-mock` to `patch` the underlying LangChain class (e.g., `patch("agent.clients.anthropic_client.ChatAnthropic")`) to ensure tests are hermetic and do not make real network calls. The test should verify that the `invoke` and `with_structured_output` methods on the mocked object are called correctly.

**USAGE MANDATE FOR LANGGRAPH NODES:**

*   Any LangGraph node that requires LLM interaction (e.g., `generate_insights_node`) MUST NOT instantiate `AnthropicClient` or `GoogleAIClient` directly. It MUST import and call the `get_llm_client` factory to get an instance of the abstract `LLMClient`. This is non-negotiable for maintaining a decoupled architecture.

**END OF MACHINE MANDATE**

