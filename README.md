# Lucid-Helix AI CLI Tools

Welcome to the Lucid-Helix AI CLI Tools! These command-line interfaces leverage the powerful AI services provided by Lucid-Helix to help you with various development tasks.

Our API services are LIVE and accessible at: **https://cet-temporal-therapist-forgot.trycloudflare.com**

## Available Tools

Here's a list of the CLI tools currently available:

### 1. API Test Tool (`api_test_tool.py`)
This tool allows you to test the various API endpoints of Lucid-Helix.
- **Description:** Send requests to different API services (chat, translate, summarize, etc.) and view the responses.
- **Usage:** `python3 api_test_tool.py <service_name> <input_text>`
  (Refer to the script for specific service names and arguments.)

### 2. Smart Code Reviewer (`smart_code_reviewer.py`)
Get intelligent code reviews for your Python files.
- **Description:** Submit a Python file for AI-powered code review, receiving suggestions for improvements, bug fixes, and best practices.
- **Usage:** `python3 smart_code_reviewer.py <path_to_python_file>`

### 3. Documentation Generator (`doc_generator.py`)
Automatically generate documentation for your code.
- **Description:** Provide a code snippet or file, and this tool will generate comprehensive documentation for it.
- **Usage:** `python3 doc_generator.py <path_to_code_file_or_snippet>`

### 4. Code Generator CLI (`code_generator_cli.py`)
Generate code snippets or full functions based on your natural language descriptions.
- **Description:** Describe what you want to build, and the AI will generate the corresponding code.
- **Usage:** `python3 code_generator_cli.py "<your_code_description>"`

### 5. Bug Fixer CLI (`bug_fixer_cli.py`)
Get AI assistance in identifying and fixing bugs in your code.
- **Description:** Provide a code snippet or file with a bug, and the AI will suggest a fix.
- **Usage:** `python3 bug_fixer_cli.py <path_to_buggy_code_file>`

## How to Use

1.  **Clone the Repository (if applicable):** If these tools are part of a larger repository, clone it to your local machine.
2.  **Install Dependencies:** Ensure you have `requests` installed (`pip install requests`).
3.  **Run the Scripts:** Execute the scripts directly using `python3 <script_name.py>` followed by the required arguments.

---

**Lucid-Helix: Your AI-powered development assistant.**