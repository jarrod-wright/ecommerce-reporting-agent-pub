# **STRIDE Threat Model v1.0**
**E-commerce Performance Reporting Agent**

**Document ID:** THREAT-MODEL-V1  
**Status:** as-built v1  
**Created:** 2025-08-29  
**Framework:** STRIDE Threat Modeling  
**AI Defense Reference:** AI Agent Defense (OWASP LLM Top 10-aligned)

---

## **Executive Summary**

This document presents a formal STRIDE threat analysis of our E-commerce Performance Reporting Agent, a LangGraph-powered AI system that processes Shopify and Google Analytics data to generate automated business intelligence reports. The analysis identifies potential security threats across all system components and evaluates existing security countermeasures against the OWASP Top 10 for LLM Applications.

**Key Findings:**
- **Critical Risks:** Prompt injection, excessive agency, and sensitive information disclosure remain the highest priority threats
- **Strong Defense Posture:** HMAC request signing, rate limiting, global exception handling, and `bleach` HTML output sanitization provide robust foundational security
- **Architectural Gaps:** HTML output sanitization is implemented; the `presidio` PII-scrubbing layer is implemented and unit-tested but **not yet wired** into the request/agent flow — a documented residual for a later sprint

---

## **System Architecture Overview**

### **Core Components Identified**
1. **FastAPI Web Service** (`src/main.py`) - HTTP API gateway with middleware stack
2. **LangGraph Agent Core** (`src/agent/graph/builder.py`) - Multi-node AI workflow engine
3. **LLM Client Layer** (`src/agent/clients/`) - Anthropic Claude and Google AI integrations
4. **Data Processing Pipeline** (Graph nodes) - Shopify/GA4 data ingestion and transformation
5. **Streamlit Frontend** (`src/streamlit_app/`) - User interface for report generation
6. **Configuration System** (`src/agent/config.py`) - Environment-based settings management

### **Trust Boundaries**
- **External → API Gateway:** Public internet to FastAPI service
- **API Gateway → Agent Core:** Validated requests to LangGraph execution
- **Agent Core → LLM Providers:** Internal system to external AI services
- **Agent Core → Data Sources:** Internal system to Shopify/GA4 APIs
- **Frontend → Backend:** Streamlit UI to FastAPI service

### **Data Flows**
1. User request → FastAPI → LangGraph Agent → External APIs → Report generation
2. Configuration data → Environment variables → Application runtime
3. Agent state persistence → LangGraph checkpointer (not yet implemented)
4. Structured logging → Internal observability systems

---

## **STRIDE Threat Analysis**

| Threat Category (STRIDE) | Component | Threat Scenario | Existing Mitigation | Proposed Hardening (Task ID) |
|-------------------------|-----------|-----------------|-------------------|------------------------------|
| **Spoofing** | FastAPI API Gateway | Attacker impersonates legitimate client to access reporting endpoints | HMAC Signature Middleware (`agent/api/middleware/request_signing.py:17-30`) validates cryptographic request signatures | Consider JWT authentication for user identity (Future enhancement) |
| **Spoofing** | LLM Client Layer | Malicious actor intercepts or spoofs LLM API credentials | API keys loaded from environment variables (`agent/config.py:18-19`), not hardcoded | Rotate to dedicated secret management service (Future enhancement) |
| **Tampering** | FastAPI Request Processing | Attacker modifies request payloads to inject malicious data | Pydantic input validation (`main.py:23-48`) with strict field constraints and `extra="forbid"` | **Implement PII Scrubbing Layer (Chunk 2)** |
| **Tampering** | LangGraph Agent State | Prompt injection via user input manipulates agent behavior to perform unintended actions | Input validation at API layer, structured message segregation planned | **Implement PII Scrubbing Layer (Chunk 2)** |
| **Tampering** | Data Processing Pipeline | Attacker injects malicious content into Shopify/GA4 data feeds that gets processed by agent | No current sanitization of external data sources | **Implement PII Scrubbing Layer (Chunk 2)** |
| **Repudiation** | All Components | User denies performing critical actions due to lack of audit trail | Structured logging with correlation IDs (`main.py:95-99`) using structlog framework | Enhance logging with user attribution (Future enhancement) |
| **Repudiation** | Agent Execution | Unable to trace agent decision-making process for compliance review | Basic node-level logging in graph execution | **Implement Human-in-the-Loop Gateway (Chunk 4)** for critical actions |
| **Information Disclosure** | Global Exception Handler | Unhandled exceptions leak sensitive system information to users | Global exception handler (`main.py:214-248`) returns generic error messages | ✅ **Already Implemented** - Structured error handling |
| **Information Disclosure** | LLM Output Processing | Agent accidentally includes PII or sensitive data in generated reports | No current output sanitization implemented | **Implement PII Scrubbing Layer (Chunk 2)** |
| **Information Disclosure** | LLM Output Processing | Agent output contains malicious JavaScript/HTML that executes in user browsers | ✅ HTML sanitization via `bleach.clean` (`src/agent/models/insights.py`, `src/main.py`) | ✅ **Implemented** - Secure Output Handling |
| **Information Disclosure** | Configuration System | API keys or secrets exposed through error messages or logs | Secrets loaded from environment, structured logging filters sensitive data | ✅ **Already Implemented** - Secure configuration loading |
| **Denial of Service** | FastAPI API Gateway | Attacker overwhelms service with high-frequency requests | Rate limiting middleware (`main.py:62-73`) with slowapi - 100 requests/minute default | ✅ **Already Implemented** - Rate limiting active |
| **Denial of Service** | LangGraph Agent | Resource exhaustion via complex agent execution workflows | Pydantic field length limits (`main.py:30-44`) prevent excessively large inputs | Consider execution timeouts for agent workflows (Future enhancement) |
| **Denial of Service** | LLM API Calls | Attacker triggers expensive LLM API calls leading to cost exhaustion | Input length validation limits token consumption exposure | Consider LLM usage quotas per user (Future enhancement) |
| **Elevation of Privilege** | Agent Tool System | Agent tools have excessive permissions allowing unintended data access | Current tools are read-only for Shopify/GA4 data retrieval | **Implement Human-in-the-Loop Gateway (Chunk 4)** for high-risk operations |
| **Elevation of Privilege** | FastAPI Authorization | Authenticated user performs actions beyond their intended scope | No current user authentication/authorization system implemented | Implement role-based access control (Future enhancement) |
| **Elevation of Privilege** | LangGraph State Management | Corrupted agent state leads to privilege escalation across user sessions | No persistent state management currently implemented | **Formal State Schema Validation** when checkpointers added |

---

## **AI-Specific Threat Assessment**

### **OWASP LLM Application Threats**

| OWASP ID | Threat | Severity | Current Status | Mitigation Plan |
|----------|--------|----------|----------------|-----------------|
| **LLM01** | Prompt Injection | **Critical** | ⚠️ **Partial** - Pydantic field validation + `bleach` input cleaning active; a `presidio` PII-scrubbing helper (`src/agent/utils/pii_scrubber.py`) is implemented and unit-tested but **not yet wired** into the request/agent flow | Wire the PII scrubbing layer into input handling; add prompt-segregation patterns |
| **LLM02** | Insecure Output Handling | **High** | ✅ **Mitigated** - HTML output sanitization via `bleach.clean` in `src/agent/models/insights.py` and `src/main.py` | Monitoring for refinement |
| **LLM04** | Model Denial of Service | **Medium** | ✅ **Mitigated** - Rate limiting + input length constraints | Monitoring for refinement |
| **LLM05** | Supply Chain Vulnerabilities | **High** | ⚠️ **Partial** - Poetry lockfile; CI runs `ruff`/`pytest` but no automated dependency scanning (deferred to a later sprint) | Add dependency vulnerability scanning |
| **LLM06** | Sensitive Information Disclosure | **High** | ⚠️ **Partial** - `presidio` PII-scrubbing helper (`src/agent/utils/pii_scrubber.py`) is implemented and unit-tested but **not yet wired** into the pipeline; output HTML is `bleach`-sanitized | **Documented limitation:** wire PII detection/redaction before LLM processing and into report output |
| **LLM07** | Insecure Plugin Design | **High** | ✅ **Low Risk** - Current tools are read-only with Pydantic schemas | Maintain strict tool design principles |
| **LLM08** | Excessive Agency | **Critical** | ✅ **Low Risk** - No state-changing tools currently | **Chunk 4: HITL Gateway** for future expansion |
| **LLM09** | Overreliance | **Medium** | ⚠️ **Partial** - No source citation or validation | Implement cross-validation patterns |

---

## **Risk Prioritization Matrix**

### **Immediate Action Required (Sprint Chunks 2-4)**
1. **LLM01 (Prompt Injection)** - Implement PII scrubbing layer with input sanitization
2. **LLM06 (Information Disclosure)** - Deploy PII redaction before LLM processing  
3. **LLM02 (Insecure Output Handling)** - Add HTML sanitization to output models
4. **LLM08 (Excessive Agency)** - Establish HITL architectural patterns

### **Strong Existing Controls**
1. **API4 (DoS)** - Rate limiting middleware with slowapi
2. **API7 (Server-Side Request Forgery)** - Request signing with HMAC validation
3. **API8 (Security Misconfiguration)** - Comprehensive security headers middleware
4. **Error Handling** - Global exception handler prevents information leakage

### **Future Enhancements**
1. User authentication and RBAC system
2. LLM usage quotas and monitoring
3. Advanced audit logging with user attribution
4. Automated dependency vulnerability scanning

---

## **Implementation Status Dashboard**

| Security Control | Implementation Status | Location | Sprint Reference |
|-------------------|---------------------|----------|------------------|
| HMAC Request Signing | ✅ **Implemented** | `agent/api/middleware/request_signing.py` | Pre-existing |
| Rate Limiting | ✅ **Implemented** | `main.py:62-73` | Pre-existing |
| Global Exception Handler | ✅ **Implemented** | `main.py:214-248` | Pre-existing |
| Input Validation | ✅ **Implemented** | `main.py:23-48` | Pre-existing |
| Security Headers | ✅ **Implemented** | `main.py:79-117` | Pre-existing |
| PII Scrubbing Layer | ⚠️ **Implemented, not wired** | `src/agent/utils/pii_scrubber.py` (unit-tested; not yet invoked in the flow) | **Chunk 2** |
| HTML Output Sanitization | ✅ **Implemented** | `src/agent/models/insights.py`, `src/main.py` (via `bleach`) | **Chunk 3** |
| Human-in-the-Loop Gateway | ⚠️ **Pending** | `agent/graph/builder.py` (architectural pattern) | **Chunk 4** |

---

## **Compliance and Audit Requirements**

### **Documentation Standards**
- ✅ Formal STRIDE analysis completed per the STRIDE methodology
- ✅ AI-specific threats assessed per OWASP LLM Top 10 guidance  
- ✅ Implementation gaps identified with sprint references
- ✅ Risk prioritization aligned with business impact

### **Continuous Monitoring**
- Track implementation of Chunks 2-4 security enhancements
- Regular re-evaluation of threat model with architecture changes
- Integration of automated security scanning in CI/CD pipeline
- Quarterly review of AI threat landscape and OWASP updates

---

## **Conclusion**

The E-commerce Performance Reporting Agent demonstrates a strong foundational security posture with comprehensive API-level protections. As built, HMAC request signing, rate limiting, global exception handling, and `bleach` HTML output sanitization (LLM02) are active. The primary residual centers on wiring the implemented `presidio` PII-scrubbing layer into the request/agent flow (LLM01, LLM06).

**Immediate Risk Mitigation:** Wiring the existing PII scrubbing layer into input handling and report output will address the remaining prompt-injection and information-disclosure residuals - providing maximum security impact per development effort invested.

**Strategic Direction:** The planned Human-in-the-Loop gateway (Chunk 4) establishes the architectural foundation for safe expansion of agent capabilities while maintaining security boundaries.

This threat model will be updated following completion of each sprint chunk to reflect the evolving security posture.

---

**Document Control:**
- **Next Review Date:** Post-Chunk 2 Implementation