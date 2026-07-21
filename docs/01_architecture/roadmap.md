# E-commerce Performance Report Agent: Implementation Roadmap

## Overview

This roadmap translates the architectural blueprint into a structured sequence of development milestones. Each milestone follows Test-Driven Development (TDD) principles and adheres to the Golden Standard Stack requirements.

**Architecture Foundation:** LangGraph-powered agent with FastAPI web service, Streamlit frontend, deployed on Google Cloud Run.

---

## Milestone 1: Foundation & Project Setup

### Objective
Establish the foundational project structure, dependency management, and development environment according to the mandated project constitution.

### Tasks
1. **Initialize Poetry Project Structure**
   - Create `pyproject.toml` with Golden Standard Stack dependencies:
     - `langgraph`, `langchain`, `langchain-anthropic`
     - `fastapi`, `uvicorn`, `streamlit`  
     - `polars`, `pydantic`, `structlog`
     - `shopify-python-api`, `google-analytics-data`
     - `plotly`, `weasyprint`, `jinja2`
   - Configure Ruff formatting rules
   - Set up `pytest`, `pytest-mock`, `pytest-asyncio` for testing

2. **Create Mandated Directory Structure**
   - `agent/clients/` - API client classes
   - `agent/tools/` - LangChain tool definitions  
   - `agent/graph/` - LangGraph node implementations
   - `agent/models/` - Pydantic data models
   - `tests/` - Test suite with matching structure
   - `templates/` - Jinja2 HTML templates
   - `streamlit_app/` - Interactive frontend

3. **Configure Development Environment**
   - Create `docker-compose.yml` for local development
   - Set up `.env.example` with required environment variables
   - Configure GitHub Actions for CI/CD pipeline

### Deliverable
Complete project scaffold with all directories, `pyproject.toml` configured, and development environment ready.

### Verification Method
- `poetry install` executes without errors
- `poetry run ruff check` passes
- `poetry run pytest --collect-only` discovers test structure
- All mandated directories exist and are importable

---

## Milestone 2: Core Data Models & State Schema

### Objective
Implement the Pydantic-based AgentState schema and supporting data models that serve as the single source of truth for the LangGraph workflow.

### Tasks
1. **Create AgentState Schema** (`agent/models/state.py`)
   - Implement `ReportingAgentState` as Pydantic BaseModel
   - Include all fields from blueprint: `report_config`, `raw_shopify_data`, `raw_ga4_data`, `processed_dataframe_json`, `generated_insights`, `visualization_filepaths`, `final_report_path`, `error_message`
   - Add proper field descriptions and validation rules

2. **Create Supporting Data Models** (`agent/models/insights.py`)
   - Implement `ReportInsights` Pydantic model for structured LLM output
   - Include `executive_summary`, `key_takeaways`, `actionable_recommendations`
   - Add validation constraints and field descriptions

3. **Create Configuration Models** (`agent/models/config.py`)
   - Implement `ReportConfig` for input validation
   - Include date range, report title, and other parameters
   - Add custom validators for date formats and business logic

### Deliverable
Complete set of Pydantic models with comprehensive validation, ready for LangGraph integration.

### Verification Method
- **TDD Test Suite:** `tests/test_models.py`
  - Test state transitions and field validation
  - Test serialization/deserialization of complex nested data
  - Test edge cases and error conditions
- `poetry run pytest tests/test_models.py -v`

---

## Milestone 3: API Client Layer

### Objective
Build secure, testable API clients for Shopify Admin API and Google Analytics Data API (GA4) with proper error handling and logging.

### Tasks
1. **Shopify API Client** (`agent/clients/shopify_client.py`)
   - Implement `ShopifyClient` class using offline access tokens
   - Methods: `fetch_orders()`, `fetch_products()`, `get_store_info()`
   - Integrate with structlog for comprehensive logging
   - Handle API rate limiting and pagination
   - Environment-based credential management

2. **Google Analytics API Client** (`agent/clients/ga4_client.py`)
   - Implement `GA4Client` class using service account authentication
   - Methods: `fetch_sessions_data()`, `fetch_user_metrics()`
   - Support custom date ranges and dimensions
   - Handle quota limits and retry logic
   - JSON credential parsing from environment

3. **Client Base Class** (`agent/clients/base_client.py`)
   - Abstract `BaseAPIClient` with common patterns
   - Standardized error handling and logging
   - Retry logic with exponential backoff
   - Request/response validation

### Deliverable
Production-ready API clients with comprehensive error handling, logging, and rate limiting.

### Verification Method
- **TDD Test Suite:** `tests/test_clients.py`
  - Mock external API calls using `pytest-mock`
  - Test authentication flows and error scenarios
  - Test rate limiting and retry behavior
  - Validate data transformation and parsing
- `poetry run pytest tests/test_clients.py -v`

---

## Milestone 4: LangChain Tools Layer

### Objective
Create LangChain tools that wrap the API clients, enabling seamless integration with the LangGraph workflow.

### Tasks
1. **Shopify Data Tool** (`agent/tools/shopify_tools.py`)
   - Implement `@tool` decorated `get_shopify_data()` function
   - Accept parameters: shop_url, date_since, access_token
   - Return structured data compatible with AgentState
   - Include comprehensive docstrings for LLM understanding

2. **GA4 Data Tool** (`agent/tools/ga4_tools.py`)
   - Implement `@tool` decorated `get_ga4_data()` function  
   - Accept parameters: property_id, credentials, start_date, end_date
   - Support multiple dimensions and metrics
   - Format output for downstream processing

3. **Tool Registry** (`agent/tools/__init__.py`)
   - Centralized registration of all available tools
   - Tool validation and schema verification
   - Easy import for LangGraph nodes

### Deliverable
LangChain-compatible tools with proper schemas, ready for agent integration.

### Verification Method
- **TDD Test Suite:** `tests/test_tools.py`
  - Test tool schema inference from type hints
  - Mock underlying client calls
  - Validate tool output format and structure
  - Test error propagation from clients to tools
- `poetry run pytest tests/test_tools.py -v`

---

## Milestone 5: LangGraph Node Implementation

### Objective
Implement the core ETL-like workflow nodes that orchestrate data fetching, processing, analysis, and report generation.

### Tasks
1. **Start Node** (`agent/graph/start_node.py`)
   - Validate `report_config` input parameters
   - Initialize logging context for the workflow
   - Set up initial state with default values

2. **Data Fetching Node** (`agent/graph/fetch_data_node.py`)
   - Orchestrate concurrent API calls to Shopify and GA4
   - Use asyncio for parallel execution
   - Populate `raw_shopify_data` and `raw_ga4_data` in state
   - Comprehensive error handling and logging

3. **Data Processing Node** (`agent/graph/process_data_node.py`)
   - Transform raw JSON data into unified Polars DataFrame
   - Clean, standardize, and merge data sources
   - Serialize processed DataFrame to JSON string
   - Store in `processed_dataframe_json` state field

4. **Insight Generation Node** (`agent/graph/generate_insights_node.py`)
   - Format DataFrame for LLM context
   - Call Claude 3.5 Sonnet with structured output schema
   - Populate `generated_insights` with validated JSON
   - Handle LLM errors and retry logic

5. **Visualization Node** (`agent/graph/generate_visualizations_node.py`)
   - Create Plotly charts from processed data
   - Generate static PNG images using Kaleido engine
   - Store image file paths in `visualization_filepaths`
   - Support multiple chart types and styling

6. **Report Compilation Node** (`agent/graph/compile_report_node.py`)
   - Render Jinja2 HTML template with insights and charts
   - Convert HTML to PDF using WeasyPrint
   - Save final report and update `final_report_path`
   - Clean up temporary files

7. **Error Handling Node** (`agent/graph/handle_error_node.py`)
   - Centralized error processing and logging
   - Optional notification sending (email/Slack)
   - Graceful workflow termination

### Deliverable
Complete set of LangGraph nodes implementing the full ETL workflow with proper error handling.

### Verification Method
- **TDD Test Suite:** `tests/test_nodes.py`
  - Test each node with mock data and dependencies
  - Validate state transitions and updates
  - Test error conditions and recovery
  - Verify logging output and structured data
- `poetry run pytest tests/test_nodes.py -v`

---

## Milestone 6: Graph Assembly & Error Handling

### Objective
Wire all nodes together into a coherent LangGraph workflow with conditional edges and robust error handling.

### Tasks
1. **Graph Builder** (`agent/graph/builder.py`)
   - Initialize StateGraph with `ReportingAgentState`
   - Register all node functions with descriptive names
   - Define normal edges for success path workflow

2. **Conditional Edge Functions** (`agent/graph/routing.py`)
   - Implement routing functions that inspect state for errors
   - Route to error handling node when `error_message` is populated
   - Continue success path when no errors detected

3. **Main Agent Factory** (`agent/agent.py`)
   - Compile complete graph into executable agent
   - Configure checkpointing for resumable workflows
   - Export agent factory function for FastAPI integration

### Deliverable
Fully assembled LangGraph agent with conditional error routing and state persistence.

### Verification Method
- **Integration Test Suite:** `tests/test_agent_integration.py`
  - End-to-end workflow testing with mock data
  - Error injection testing to validate routing
  - State persistence and resumption testing
  - Performance and timeout testing
- `poetry run pytest tests/test_agent_integration.py -v`

---

## Milestone 7: LLM Integration & Structured Output

### Objective
Implement robust Claude 3.5 Sonnet integration using tool-use pattern for reliable structured output generation.

### Tasks
1. **LLM Client** (`agent/clients/llm_client.py`)
   - Initialize ChatAnthropic with Claude 3.5 Sonnet
   - Configure structured output binding with Pydantic models
   - Implement retry logic for API failures
   - Environment-based API key management

2. **Prompt Templates** (`agent/prompts/templates.py`)
   - Create optimized prompts for e-commerce analysis
   - Include clear instructions for structured output
   - Support dynamic data insertion and formatting
   - Version control for prompt iterations

3. **LLM Tool Integration** (`agent/tools/llm_tools.py`)
   - Wrap LLM calls in LangChain tool interface
   - Handle structured output validation and conversion
   - Implement fallback strategies for malformed responses

### Deliverable
Production-ready LLM integration with guaranteed structured output conforming to `ReportInsights` schema.

### Verification Method
- **TDD Test Suite:** `tests/test_llm_integration.py`
  - Mock LLM responses for consistent testing
  - Test structured output validation
  - Test error handling and retry logic
  - Validate prompt template rendering
- `poetry run pytest tests/test_llm_integration.py -v`

---

## Milestone 8: Visualization & PDF Generation

### Objective
Implement high-quality data visualizations and professional PDF report generation using the HTML-first pattern.

### Tasks
1. **Chart Generation** (`agent/visualization/charts.py`)
   - Implement Plotly chart creation functions
   - Support multiple chart types: time series, pie charts, bar graphs
   - Export to PNG using Kaleido engine with consistent styling
   - Base64 encoding for HTML embedding

2. **HTML Templates** (`templates/report_template.html`)
   - Professional report layout with CSS styling
   - Responsive design for various content lengths
   - Placeholder integration for dynamic content
   - Support for embedded base64 images

3. **PDF Generator** (`agent/reports/pdf_generator.py`)
   - WeasyPrint integration for HTML-to-PDF conversion
   - Custom CSS for print optimization
   - Font and styling configuration
   - Memory-efficient processing for serverless environments

### Deliverable
Complete visualization and PDF generation system producing professional-quality reports.

### Verification Method
- **TDD Test Suite:** `tests/test_visualization.py`, `tests/test_pdf_generation.py`
  - Test chart generation with sample data
  - Validate PDF output structure and content
  - Test template rendering with various data scenarios
  - Verify memory usage and performance
- `poetry run pytest tests/test_visualization.py tests/test_pdf_generation.py -v`

---

## Milestone 9: FastAPI Web Service

### Objective
Create the FastAPI web service that exposes the LangGraph agent as a RESTful API for both scheduled execution and interactive use.

### Tasks
1. **Main FastAPI Application** (`main.py`)
   - Initialize FastAPI app with proper configuration
   - Implement health check endpoint
   - Configure CORS and middleware as needed
   - Environment-based configuration management

2. **Agent Endpoints** (`api/agent_routes.py`)
   - `/generate-report` POST endpoint for triggering agent
   - Request/response models using Pydantic
   - Async execution with proper error handling
   - Progress tracking and status reporting

3. **Cloud Scheduler Integration** (`api/scheduler_routes.py`)
   - Dedicated endpoint for Cloud Scheduler triggers
   - OIDC token validation for security
   - JSON payload processing for flexible configuration
   - Logging and monitoring integration

### Deliverable
Production-ready FastAPI web service exposing the agent via RESTful endpoints.

### Verification Method
- **API Test Suite:** `tests/test_api.py`
  - Test all endpoints with various payloads
  - Test authentication and authorization
  - Test concurrent request handling
  - Validate response formats and error codes
- `poetry run pytest tests/test_api.py -v`
- Manual testing with `poetry run uvicorn main:app --reload`

---

## Milestone 10: Streamlit Interactive Frontend

### Objective
Build an intuitive Streamlit interface for on-demand report generation, testing, and demonstration purposes.

### Tasks
1. **Main Streamlit App** (`streamlit_app/app.py`)
   - Clean, professional interface design
   - Report generation trigger with progress indicators
   - Session state management for report data
   - Download button for generated PDFs

2. **Configuration Interface** (`streamlit_app/config.py`)
   - Date range selection widgets
   - Report customization options
   - API connection testing utilities
   - Environment configuration validation

3. **Report Viewer** (`streamlit_app/viewer.py`)
   - Inline preview of generated insights
   - Chart display and interaction
   - Historical report access
   - Performance metrics dashboard

### Deliverable
User-friendly Streamlit application providing full access to agent functionality.

### Verification Method
- **Frontend Test Suite:** `tests/test_streamlit.py`
  - Test UI components and interactions
  - Test session state management
  - Test download functionality
  - Validate error handling in UI
- Manual testing: `poetry run streamlit run streamlit_app/app.py`

---

## Milestone 11: Containerization & Infrastructure

### Objective
Package the application in Docker containers and configure Google Cloud deployment infrastructure.

### Tasks
1. **Multi-stage Dockerfile**
   - Builder stage with WeasyPrint system dependencies
   - Production stage with minimal footprint
   - Poetry-based dependency management
   - Security hardening and non-root execution

2. **Cloud Run Configuration** (`cloudbuild.yaml`)
   - Automated build and deployment pipeline
   - Secret Manager volume mounts configuration
   - Service account and IAM role assignments
   - Environment variable and scaling configuration

3. **Infrastructure as Code** (`infrastructure/`)
   - Terraform modules for GCP resources
   - Secret Manager secret definitions
   - Cloud Scheduler job configuration
   - IAM policies and service account setup

### Deliverable
Complete containerization and infrastructure setup ready for production deployment.

### Verification Method
- **Container Test Suite:** `tests/test_container.py`
  - Test Docker image builds successfully
  - Test application startup in container
  - Test volume mounts and secret access
  - Validate resource usage and performance
- `docker build -t ecommerce-agent .`
- `docker run -p 8080:8080 ecommerce-agent`

---

## Milestone 12: Observability & Production Readiness

### Objective
Implement comprehensive observability, monitoring, and production-ready features including LangSmith integration.

### Tasks
1. **LangSmith Integration** (`agent/observability/langsmith.py`)
   - Environment-based LangSmith configuration
   - Automatic tracing for all LangGraph executions
   - Custom evaluators for output quality
   - Dataset creation for regression testing

2. **Structured Logging** (`agent/observability/logging.py`)
   - Standardized logging format across all components
   - Correlation IDs for request tracking
   - Performance metrics and timing
   - Error aggregation and alerting

3. **Health Checks & Monitoring** (`api/health.py`)
   - Comprehensive health check endpoints
   - Dependency validation (APIs, secrets, etc.)
   - Performance metrics collection
   - Integration with Cloud Run health checks

4. **Production Testing Suite** (`tests/test_production.py`)
   - End-to-end integration tests
   - Performance and load testing
   - Security vulnerability scanning
   - Compliance and audit logging validation

### Deliverable
Production-ready application with comprehensive observability, monitoring, and quality assurance.

### Verification Method
- **Production Test Suite:** `tests/test_production.py`
  - End-to-end workflow validation
  - Performance benchmarking
  - Security scanning and validation
  - Observability and monitoring verification
- `poetry run pytest tests/test_production.py -v`
- LangSmith dashboard validation
- Cloud Run deployment and health check validation

---

## Success Criteria & Definition of Done

Each milestone is considered complete when:

1. **All tests pass:** `poetry run pytest` returns 0 exit code
2. **Code quality standards:** `poetry run ruff check --fix && poetry run ruff format` passes
3. **Documentation complete:** All functions, classes, and modules have docstrings
4. **Integration validated:** Components work together as designed
5. **Performance verified:** Meets response time and resource usage requirements

## Risk Mitigation

- **API Rate Limits:** Implement robust retry logic and request queuing
- **LLM Reliability:** Fallback strategies for malformed responses
- **Container Resources:** Memory optimization for serverless constraints
- **Security:** Regular dependency updates and vulnerability scanning
- **Data Privacy:** Ensure no sensitive data persists in logs or temporary files

## Timeline Estimate

- **Milestones 1-3:** Foundation (1-2 weeks)
- **Milestones 4-6:** Core Agent (2-3 weeks)
- **Milestones 7-9:** AI Integration & API (2-3 weeks)
- **Milestones 10-12:** Frontend & Production (1-2 weeks)

**Total Estimated Duration:** 6-10 weeks for complete implementation