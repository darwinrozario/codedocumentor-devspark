# Code Auto-Documenter Project Documentation

This document provides a comprehensive overview and detailed documentation for the Code Auto-Documenter project.  The project aims to automate the generation of code documentation using an AI-powered approach, leveraging the Gemini API.

## 1. Project Overview

**Purpose and Goals:** The Code Auto-Documenter simplifies the process of creating comprehensive code documentation. It takes source code files (individual files or entire projects within ZIP archives) or GitHub repository URLs as input and generates detailed documentation in HTML format. The project also incorporates an AI-powered chatbot for interactive exploration of the generated documentation.

**Technology Stack and Architecture:**

- **Backend:** Python (Flask framework) for API endpoints, file processing, and Gemini API interaction.
- **Frontend:** HTML, CSS, and JavaScript (Tailwind CSS for styling) for user interface and interaction.
- **AI Model:** Google Gemini 2.5 Flash for documentation generation and chatbot responses.
- **Data Storage:** No persistent data storage is used; all processing is done in memory.

**Project Structure:**

```
code-auto-documenter/
├── app.py             # (Original) Main Flask application (basic functionality)
├── enhanced_app.py   # Enhanced Flask application with AST analysis and improved features
├── config.yaml        # Configuration file for the application
├── CHATBOT_FEATURE.md # Chatbot feature documentation
├── README.md          # (Empty) Main project README file
├── static/
│   ├── css/
│   │   └── styles.css  # CSS styles for the application
│   └── js/
│       ├── chatbot.js  # JavaScript for chatbot functionality
│       └── script.js   # Main JavaScript for file handling, documentation display, etc.
└── templates/
    └── index.html     # Main HTML template for the application
```

## 2. File Documentation

### 2.1 `app.py`

**Purpose and Overview:** This file contains the initial Flask application implementation. It provides basic functionality for uploading files, generating documentation using the Gemini API, and handling user requests.  This version lacks the advanced features found in `enhanced_app.py`.

**Key Functions/Classes:**

- `allowed_file(filename)`: Checks if a file's extension is supported.
- `should_ignore_path(path)`: Checks if a path should be ignored based on predefined patterns.
- `clone_github_repository(repo_url)`: Clones a GitHub repository, extracts supported files, and returns their contents.
- `extract_files_from_zip(zip_file)`: Extracts and processes files from an uploaded ZIP archive.
- `call_gemini_api(prompt)`: Sends a prompt to the Gemini API and returns the generated text.
- `clean_markdown_to_html(text)`: Cleans up markdown formatting and converts it to HTML.
- `create_documentation_prompt(file_contents)`: Creates the prompt for the Gemini API based on the uploaded files.
- Flask routes: `/`, `/generate-documentation`, `/analyze-github`, `/download-documentation`.

**Dependencies:** `flask`, `os`, `json`, `requests`, `zipfile`, `io`, `re`, `subprocess`, `tempfile`, `shutil`, `werkzeug`.

**Usage Examples:**  (See the Flask routes within the file for usage examples)

**Code Comments:**  The code includes inline comments explaining the purpose of various sections and functions.

**API Documentation:** (See inline docstrings within the `app.py` file)

### 2.2 `enhanced_app.py`

**Purpose and Overview:** This file contains the improved Flask application. It builds upon `app.py` by adding advanced features like AST-based code analysis for Python and JavaScript/TypeScript files, improved error handling, and more detailed metrics in the API responses.

**Key Functions/Classes:**

- `clone_github_repository(repo_url)`:  Similar to `app.py`, but includes code analysis using `CodeAnalyzer`.
- `is_supported_file(filename)`: Checks if a file extension is supported, considering both simple and language-specific extensions.
- `CodeAnalyzer`: A class that performs static code analysis using AST parsing.
    - `analyze_python_file(file_path, content)`: Analyzes Python code using `ast`.
    - `analyze_javascript_file(file_path, content)`: Performs basic analysis of JavaScript/TypeScript code using regular expressions.
- `PythonASTAnalyzer(ast.NodeVisitor)`:  An AST visitor for detailed Python code analysis.
- `allowed_file(filename)`: Improved file extension check.
- `should_ignore_path(path)`: Improved path ignoring logic.
- `extract_files_from_zip(zip_file)`:  Improved ZIP file extraction with optional code analysis.
- `call_gemini_api(prompt)`: Improved error handling and response parsing.
- `generate_style_guide_prompt(language, style)`: Generates prompts with specific style guide instructions.
- `create_documentation_prompt(file_contents, style_guide)`: Creates a more detailed prompt for Gemini, incorporating AST analysis results.
- Flask routes: `/`, `/generate-documentation`, `/analyze-github`, `/download-documentation`, `/chatbot`.

**Dependencies:** `flask`, `os`, `json`, `requests`, `zipfile`, `io`, `re`, `ast`, `astroid`, `subprocess`, `tempfile`, `shutil`, `pathlib`, `werkzeug`, `yaml`, `typing`.

**Usage Examples:** (See Flask routes within the file)

**Code Comments:** The code includes extensive comments explaining complex logic and algorithms, especially within the code analysis sections.

**API Documentation:** (See inline docstrings within the `enhanced_app.py` file)

### 2.3 `config.yaml`

**Purpose and Overview:** This YAML file stores the configuration settings for the application.  It allows customization of documentation style, output format, analysis settings, API parameters, and other options.

**Key Sections:** `style_guide`, `output`, `analysis`, `api`, `templates`, `quality`, `git`.

**Dependencies:** None (YAML parsing is handled within the Python code).

**Usage Examples:** Modify the values within the `config.yaml` file to change the application's behavior.

### 2.4 `CHATBOT_FEATURE.md`

**Purpose and Overview:** This Markdown file documents the AI-powered chatbot feature added to the Code Auto-Documenter.

**Key Sections:** Overview, Features, How to Use, Technical Implementation, Files Modified/Added, API Endpoints, Configuration, Browser Compatibility, Future Enhancements, Troubleshooting, Support.

**Dependencies:** None.

### 2.5 `README.md`

**Purpose and Overview:** This file is currently empty and should be populated with a concise overview of the project, installation instructions, and usage examples.

### 2.6 `static/css/styles.css`

**Purpose and Overview:** This CSS file contains the styles for the application's user interface.  It uses Tailwind CSS classes and custom styles for improved visual presentation.

**Dependencies:** Tailwind CSS.

### 2.7 `static/js/chatbot.js`

**Purpose and Overview:** This JavaScript file handles the chatbot's functionality, including sending messages, receiving responses from the server, and managing the chat interface.

**Dependencies:**  Fetch API.

### 2.8 `static/js/script.js`

**Purpose and Overview:** This JavaScript file handles file uploads, documentation display, copy/download functionality, fullscreen mode, and dark mode switching.

**Dependencies:**  Fetch API, Blob API, URL API, Navigator.clipboard API.

### 2.9 `templates/index.html`

**Purpose and Overview:** This HTML file is the main template for the application's user interface.  It uses Tailwind CSS for styling and includes sections for file uploads, documentation display, and the chatbot.

**Dependencies:** Tailwind CSS, Font Awesome.

## 3. Setup and Installation

1. **Prerequisites:** Python 3.7+, pip, Node.js (for optional frontend development).
2. **Installation:**
   - Clone the repository: `git clone <repository_url>`
   - Navigate to the project directory: `cd code-auto-documenter`
   - Create a virtual environment (recommended): `python3 -m venv venv`
   - Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
   - Install dependencies: `pip install -r requirements.txt`
3. **Configuration:** Obtain a Gemini API key and place it in `enhanced_app.py` (or set the `GEMINI_API_KEY` environment variable).  Customize settings in `config.yaml` as needed.

## 4. Usage Examples

1. **Upload Files:** Drag and drop code files or a ZIP archive containing your project into the designated area, or click "Browse Files" to select files manually.
2. **GitHub Analysis:** Enter a valid GitHub repository URL and click "Analyze Repository."
3. **Generate Documentation:** Click "Generate Documentation" to initiate the documentation generation process.
4. **Chatbot:** Once documentation is generated, use the chatbot to ask questions about your project.

## 5. API Reference

The main API endpoints are documented within the `enhanced_app.py` file using inline docstrings.  Key endpoints include:

- `/generate-documentation`: Generates documentation from uploaded files.
- `/analyze-github`: Analyzes a GitHub repository.
- `/download-documentation`: Downloads the generated documentation.
- `/chatbot`: Handles chatbot interactions.

Detailed parameter descriptions, return values, and potential exceptions are provided in the inline docstrings.

## 6. Contributing Guidelines

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Make your changes and commit them with clear and concise messages.
- Push your branch to your fork.
- Create a pull request to the main repository.

**Code Style:**  Follow PEP 8 for Python code and maintain consistent formatting throughout the project.

## 7.  Future Enhancements

- Improved code analysis capabilities (support for more languages, more sophisticated analysis).
- Enhanced chatbot features (contextual understanding, code execution, multi-language support).
- Integration with other documentation tools (e.g., Sphinx, JSDoc).
- User authentication and project management.
- Support for different documentation styles (e.g., Google, NumPy, JSDoc).

This documentation provides a comprehensive overview of the Code Auto-Documenter project.  Remember to consult the inline comments and docstrings within the code for more detailed information.