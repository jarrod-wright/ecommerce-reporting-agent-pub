### **Architectural Design Document: The High-Trust UI/UX Implementation (v2.0)**

**Document ID:** ADD-UIUX-POLISH-V2.0
**Purpose:** Machine-Readable Mandate for Claude Code
**Status:** FINAL

---

**START OF MACHINE MANDATE**

**PRIMARY DIRECTIVE: CONSTITUTIONAL & FRAMEWORK ADHERENCE**

1.  **Project Constitution:** Your primary directive. All code must adhere to its standards.
2.  **This Document (`ADD-UIUX-POLISH-V2.0.md`):** This is your definitive architectural specification for this milestone. You MUST implement the components and logic exactly as defined herein.
3.  **Guiding Framework:** This document provides the strategic "why" behind the mandates in this ADD. You must use it to inform the *intent* and *quality* of your implementation.

**OVERALL ARCHITECTURAL MANDATE: THE "DESIGN SYSTEM" PATTERN**

Your core task is to refactor the `streamlit_app` into a modular, component-based architecture. You will create a centralized theme, a library of reusable UI components, and a main application file that acts as an orchestrator. Direct, un-styled calls to `st` components from `app.py` are now an anti-pattern.

---

### **SECTION 1: THE THEME MODULE**

**File Path:** `streamlit_app/theme.py`

**Objective:** To create a single, version-controlled source of truth for all visual styling.

**Instructions:**
1.  Create the file `streamlit_app/theme.py`.
2.  Populate it with the following Python dictionaries. The keys and hex codes are non-negotiable.

**Content:**
```python
# streamlit_app/theme.py

COLORS = {
    "PRIMARY": "#2563EB",
    "SURFACE": "#FFFFFF",
    "SURFACE_ALT": "#F8FAFC",
    "TEXT_PRIMARY": "#1A202C",
    "TEXT_SECONDARY": "#475569",
    "BORDER": "#CBD5E1",
    "SUCCESS": "#16A34A",
    "WARNING": "#F59E0B",
    "ERROR": "#DC2626",
}

# NOTE: Actual font rendering is controlled by st.markdown CSS.
# This dictionary is for reference and potential future use.
FONTS = {
    "TITLE": "Poppins, sans-serif",
    "BODY": "Inter, sans-serif",
}
```

---

### **SECTION 2: GLOBAL APPLICATION CONFIGURATION & STYLING**

**File Path:** `streamlit_app/config.py` (New File)

**Objective:** To create a centralized module for global application settings and to inject custom CSS for styling.

**Instructions:**
1.  Create the file `streamlit_app/config.py`.
2.  Implement a function `configure_page()` that will be called at the start of `app.py`.
3.  This function MUST use `st.set_page_config` to apply the mandated "wide" layout.
4.  This function MUST contain a block of custom CSS injected via `st.markdown(..., unsafe_allow_html=True)`. This CSS will enforce our typography and other custom styles not natively available in Streamlit.

**Content:**
```python
# streamlit_app/config.py

import streamlit as st

def configure_page():
    """Sets the page configuration and injects custom CSS for the app."""
    
    # --- Page Config ---
    st.set_page_config(
        page_title="AI Software Factory | E-commerce BI Agent",
        layout="wide"
    )

    # --- Custom CSS Injection ---
    # This injects our custom font and other styles.
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600&display=swap');
            
            /* General Body Font */
            html, body, [class*="st-"] {
                font-family: 'Inter', sans-serif;
            }

            /* Title Font */
            h1 {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                letter-spacing: -0.5px;
            }

            /* Header Font */
            h2 {
                font-family: 'Poppins', sans-serif;
                font-weight: 500;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
```

---

### **SECTION 3: THE COMPONENT LIBRARY**

**Objective:** To build a library of reusable, standardized UI components.

#### **3.1 Header Component**

**File Path:** `streamlit_app/components/header.py` (New File)

**Instructions:**
1.  Create the file `streamlit_app/components/header.py`.
2.  Create a function `render_header()`.
3.  This function is responsible ONLY for rendering the main title and subheader of the application.

**Content:**
```python
# streamlit_app/components/header.py

import streamlit as st

def render_header():
    """Renders the main application header and title."""
    
    st.title("E-commerce Performance Report Agent")
    st.subheader("Your AI-powered business intelligence partner for Shopify & GA4.")
    st.divider()

```

Of course. Executing Turn 2.

Here is the complete Part 2 of our definitive, machine-readable architectural document.

---

### **Architectural Design Document: The High-Trust UI/UX Implementation (v2.0)**

---

### **Part 2: The Machine-Readable Mandate (For Claude Code)**

**START OF MACHINE MANDATE**

---

#### **3.2 Feedback Component**

**File Path:** `streamlit_app/components/feedback.py` (New File)

**Objective:** To encapsulate the logic for displaying standardized, user-facing status messages, adhering to Mandate 3.2 of the UX Playbook.

**Instructions:**
1.  Create the file `streamlit_app/components/feedback.py`.
2.  Implement two functions, `display_success_message` and `display_error_message`, exactly as specified below.

**Content:**
```python
# streamlit_app/components/feedback.py

import streamlit as st

def display_success_message(message: str):
    """Displays a standardized success message."""
    st.success(f"✅ **Success:** {message}", icon="✅")

def display_error_message(message: str):
    """Displays a standardized error message."""
    st.error(f"❌ **Error:** {message}", icon="❌")

```

#### **3.3 Main Interaction Component**

**File Path:** `streamlit_app/components/main_interface.py` (New File)

**Objective:** To encapsulate the primary user interaction logic, including the main button and the conditional display of the download button.

**Instructions:**
1.  Create the file `streamlit_app/components/main_interface.py`.
2.  Implement a function `render_main_interface()`. This function will contain the core interactive elements of the application.

**Content:**
```python
# streamlit_app/components/main_interface.py

import streamlit as st
from ..api_client import trigger_report_generation
from .feedback import display_success_message, display_error_message

def render_main_interface():
    """Renders the main user interface for report generation."""
    
    st.header("Generate Your Report")
    
    # Mandate 3.5 (Focus) & 3.1 (Clarity)
    if st.button(
        "Generate My Report",
        type="primary",
        help="Click to run the AI analysis and generate your PDF report."
    ):
        # Mandate 3.2 (Continuous Feedback)
        with st.spinner("AI agent at work... Analyzing data and generating insights..."):
            result_bytes = trigger_report_generation(
                report_title="Weekly Performance Report",
                date_range="last_7_days"
            )

        # Mandate 3.2 (Feedback)
        if result_bytes:
            st.session_state.report_bytes = result_bytes
            display_success_message("Report generated successfully!")
        else:
            st.session_state.report_bytes = None
            display_error_message("Failed to generate report. Please try again later.")

    # Mandate: The Final Deliverable (Conditional display)
    if st.session_state.get("report_bytes"):
        st.divider()
        st.download_button(
            label="Download Full Report (PDF)",
            data=st.session_state.report_bytes,
            file_name="E-commerce_Performance_Report.pdf",
            mime="application/pdf"
        )
```

---

### **SECTION 4: THE SESSION STATE SCHEMA**

**File Path:** `streamlit_app/state.py` (New File)

**Objective:** To establish a formal, centralized schema for managing the application's session state. This is a critical Clean Code principle.

**Instructions:**
1.  Create the file `streamlit_app/state.py`.
2.  Implement a function `initialize_session_state()` that ensures all required keys exist in `st.session_state`. This prevents `KeyError` exceptions.

**Content:**
```python
# streamlit_app/state.py

import streamlit as st

def initialize_session_state():
    """Initializes all required keys in the Streamlit session state."""
    
    if "report_bytes" not in st.session_state:
        st.session_state.report_bytes = None
    
    # Add other future state keys here
    # if "user_name" not in st.session_state:
    #     st.session_state.user_name = None
```

---

### **SECTION 5: THE MAIN APPLICATION ORCHESTRATOR**

**File Path:** `streamlit_app/app.py` (To be Refactored)

**Objective:** To refactor the main application file into a clean "orchestrator" that imports and calls the standardized components.

**Instructions:**
1.  Overwrite the existing `streamlit_app/app.py`.
2.  The new version must only contain logic for importing and calling the high-level components in the correct order.

**Content:**
```python
# streamlit_app/app.py

from .config import configure_page
from .state import initialize_session_state
from .components.header import render_header
from .components.main_interface import render_main_interface

def main():
    """
    Main function to orchestrate the Streamlit application.
    """
    # 1. Set page config and styles (must be the first Streamlit command)
    configure_page()

    # 2. Initialize all session state keys
    initialize_session_state()

    # 3. Render the header component
    render_header()
    
    # 4. Render the main interactive component
    render_main_interface()

if __name__ == "__main__":
    main()
```

---

### **SECTION 6: THE TESTING DOCTRINE**

**Objective:** To define the testing strategy for this new, component-based UI architecture.

**Instructions:**
*   You must refactor the existing `tests/frontend/test_app.py`.
*   You must create new test files for each new module (`test_config.py`, `test_header.py`, etc.).
*   Tests must be simple, focused "smoke tests" that verify the structural integrity and basic functionality of each component, not the visual output.

**Test File Structure:**

*   `tests/frontend/test_config.py`: Test that `configure_page()` can be called without error.
*   `tests/frontend/test_state.py`: Test that `initialize_session_state()` correctly adds the `report_bytes` key.
*   `tests/frontend/test_header.py`: Test that `render_header()` can be called without error.
*   `tests.frontend.test_feedback.py`: Test that the feedback functions can be called without error.
*   `tests/frontend/test_main_interface.py`: This will contain the more complex test for the button-to-API-call workflow, which we will adapt from our previous `test_app.py`.

**END OF MACHINE MANDATE**