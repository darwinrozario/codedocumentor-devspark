# Code Auto-Documenter Project Documentation

## 📋 Project Overview

The Code Auto-Documenter is a web application designed to automatically generate comprehensive documentation for software projects. It leverages the Google Gemini API to analyze code and produce well-structured HTML documentation, incorporating an AI-powered chatbot for interactive assistance. The project aims to streamline the documentation process, improving code maintainability and collaboration.

### Technology Stack and Architecture

The project utilizes a client-server architecture:

* **Backend:** Flask (Python) with enhanced code analysis using Abstract Syntax Tree (AST) parsing.
* **Frontend:** HTML, CSS, JavaScript (using Tailwind CSS and Font Awesome).
* **AI Engine:** Google Gemini API for natural language processing and documentation generation.
* **Code Analysis:** AST parsing libraries (`ast` and `astroid` for Python, regex-based analysis for JavaScript/TypeScript).

The frontend handles user interaction (file uploads, GitHub repository input, documentation display, and chatbot interaction). The backend processes file uploads, clones GitHub repositories, analyzes code, calls the Gemini API, and manages API responses. The Gemini API generates the documentation based on a carefully crafted prompt incorporating code analysis results.

### Project Structure and Organization

The project's directory structure is as follows:

```
CodeAutoDocumenter/
├── app.py             # Initial Flask application (basic functionality)
├── enhanced_app.py   # Enhanced Flask application with improved code analysis and features.
├── config.yaml        # Configuration file for various settings
├── static/
│   ├── css/
│   │   └── styles.css  # Stylesheet for the web application
│   └── js/
│       ├── chatbot.js  # JavaScript file for chatbot functionality
│       └── script.js   # Main JavaScript file for frontend logic
├── templates/
│   └── index.html     # Main HTML template for the web application
├── CHATBOT_FEATURE.md # Documentation for the chatbot feature
└── README.md          # Project README file
```

## 📚 File Documentation

### 📄 app.py

#### Purpose and Overview

This file provides a basic Flask application for generating documentation using the Gemini API. It handles file uploads and GitHub repository analysis, but lacks the advanced code analysis features of `enhanced_app.py`.

#### Key Functions/Classes

| Function/Class          | Purpose                                                                     | Parameters                                      | Return Value                                   | Exceptions                                      |
|--------------------------|-----------------------------------------------------------------------------|-------------------------------------------------|-------------------------------------------------|-------------------------------------------------|
| `allowed_file(filename)` | Check if file extension is supported                                        | `filename` (str)                              | `bool`                                         | None                                           |
| `should_ignore_path(path)` | Check if path should be ignored                                             | `path` (str)                                  | `bool`                                         | None                                           |
| `clone_github_repository(repo_url)` | Clone a GitHub repository and return file contents                      | `repo_url` (str)                             | `list` of dictionaries (file name, content, extension) | Invalid URL, cloning failures, timeouts         |
| `extract_files_from_zip(zip_file)` | Extract and process files from uploaded ZIP folder                       | `zip_file` (werkzeug.datastructures.FileStorage) | `list` of dictionaries (file name, content, extension) | Processing errors                              |
| `call_gemini_api(prompt)` | Call Gemini API to generate documentation                                   | `prompt` (str)                                | `str` (generated documentation)                 | API request failures                           |
| `clean_markdown_to_html(text)` | Convert markdown formatting to proper HTML                               | `text` (str)                                 | `str` (HTML formatted text)                    | None                                           |
| `create_documentation_prompt(file_contents)` | Create the prompt for documentation generation                         | `file_contents` (list)                        | `str` (prompt)                                 | None                                           |

#### Dependencies

- Flask
- requests
- zipfile
- re
- subprocess
- tempfile
- shutil
- werkzeug
- pathlib

#### Usage Examples

The main functionality is accessed through POST requests to `/generate-documentation` and `/analyze-github`. See the code for detailed examples within the route handlers.

### 📄 enhanced_app.py

#### Purpose and Overview

This file contains the enhanced Flask application, incorporating advanced code analysis using AST parsing for Python and regex-based analysis for JavaScript/TypeScript. This improves the accuracy and comprehensiveness of the generated documentation.

#### Key Functions/Classes

- **`CodeAnalyzer`:** Analyzes code structure using AST parsing. Contains methods for Python and JavaScript/TypeScript analysis.
- **`PythonASTAnalyzer`:** Extends `ast.NodeVisitor` for detailed Python code analysis (functions, classes, imports).

##### Key Functions:

| Function/Class          | Purpose                                                                                             | Parameters                                                              | Return Value                                                                   | Exceptions                                                              |
|--------------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `is_supported_file(filename)` | Check if a file has a supported extension.                                                        | `filename` (str)                                                          | `bool`                                                                        | None                                                                   |
| `clone_github_repository(repo_url)` | Clone a GitHub repository and return file contents, including code analysis.                     | `repo_url` (str)                                                        | `list` of dictionaries (file name, content, extension, analysis)             | Invalid URL, cloning failures, timeouts                                     |
| `extract_files_from_zip(zip_file)` | Extract files from an uploaded ZIP archive, including code analysis.                               | `zip_file` (werkzeug.datastructures.FileStorage)                         | `list` of dictionaries (file name, content, extension, analysis)             | Processing errors                                                          |
| `call_gemini_api(prompt)` | Call Gemini API to generate documentation, handling various response structures for robustness.     | `prompt` (str)                                                            | `str` (generated documentation)                                             | API request failures                                                      |
| `generate_style_guide_prompt(language, style)` | Generate style guide-specific prompts.                                                            | `language` (str), `style` (str)                                          | `str` (style guide prompt)                                                  | None                                                                   |
| `create_documentation_prompt(file_contents, style_guide)` | Create the Gemini API prompt, incorporating AST analysis data.                                      | `file_contents` (list), `style_guide` (str)                             | `str` (prompt)                                                                | None                                                                   |
| `clean_markdown_to_html(text)` | Cleans up markdown formatting and converts it to HTML.                                             | `text` (str)                                                             | `str` (HTML formatted text)                                                | None                                                                   |

#### Dependencies

- Flask
- requests
- zipfile
- re
- ast
- astroid
- subprocess
- tempfile
- shutil
- pathlib
- werkzeug
- typing
- yaml

#### Usage Examples

Similar to `app.py`, but with the addition of a `style_guide` parameter to specify documentation style (e.g., 'google', 'numpy').

### 📄 config.yaml

#### Purpose and Overview

This YAML file configures various settings for the Code Auto-Documenter, including style guides, output formats, API keys, and analysis options.

#### Key Settings

The `config.yaml` file uses a hierarchical structure to organize settings.  Key sections include:

- `style_guide`:  Specifies the documentation style guide (e.g., 'google', 'numpy', 'sphinx', 'jsdoc').
- `output`: Defines output settings (format, directory, filename).
- `analysis`: Configures code analysis settings (languages, ignore patterns, ignore directories).
- `api`: Contains Gemini API key, timeout, and model configuration.
- `templates`: Provides custom prompt templates for different project types.
- `quality`: Sets quality control parameters (minimum coverage, hallucination checks, code validation).
- `git`: Configures Git integration (hooks, pre-commit checks, CI/CD).

### 📄 CHATBOT_FEATURE.md

#### Purpose and Overview

This markdown file documents the AI-powered chatbot feature, explaining its functionality, usage, technical implementation, and API endpoint.

#### Key Features

- AI-powered Q&A about generated documentation.
- Interactive chat interface with dark mode support.
- User-friendly design with color-coded messages and syntax highlighting.

### 📄 README.md

#### Purpose and Overview

This file provides a high-level overview of the project, including its purpose, architecture, and usage instructions. It also links to more detailed documentation for individual files and features.

### 📄 static/css/styles.css

#### Purpose and Overview

This CSS file styles the web application, including file upload sections, progress bars, documentation display, chatbot interface, and fullscreen mode. It also supports dark mode.  The styles are extensively commented within the file itself.

### 📄 static/js/chatbot.js

#### Purpose and Overview

This JavaScript file implements the chatbot's frontend functionality, handling user input, sending requests to the backend, receiving and displaying responses, and managing chatbot visibility.  The code is well-commented and uses modern JavaScript features.

### 📄 static/js/script.js

#### Purpose and Overview

This JavaScript file manages the main frontend logic, including file uploads, display of file lists, documentation generation requests, display of generated documentation, copy and download functionality, and fullscreen mode. It also includes a function to convert HTML to Markdown.  The code is modular and well-organized.

### 📄 templates/index.html

#### Purpose and Overview

This HTML file provides the main user interface for the Code Auto-Documenter web application. It uses Tailwind CSS for styling and includes sections for file uploads, progress display, documentation output, and the chatbot.  The HTML is well-structured and uses semantic elements.

## 🚀 Setup and Installation

### Prerequisites

- Python 3.7+
- Node.js and npm (optional, for frontend development)
- A Google Cloud Platform (GCP) project with the Gemini API enabled and a valid API key. The API key should be set as the environment variable `GEMINI_API_KEY` or within the `config.yaml` file.

### Installation Steps

1. Clone the repository: `git clone <repository_url>`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Configure `config.yaml` with your Gemini API key and other desired settings.
4. (Optional) Install Node.js and npm and run `npm install` to install frontend dependencies.
5. Run the Flask application: `python enhanced_app.py`

## 💻 Usage Examples

The application can be used in two ways:

1. **File Upload:** Upload individual code files or a zipped folder.
2. **GitHub Repository Analysis:** Provide a GitHub repository URL.

After documentation generation, you can copy the HTML or Markdown content, download it as a Markdown file, or use the integrated chatbot.

## 🔧 API Reference

The main API endpoints are:

- **`POST /generate-documentation`:** Generates documentation from uploaded files. Accepts files via multipart/form-data and a `style_guide` parameter. Returns JSON with documentation, success status, and metrics.
- **`POST /analyze-github`:** Generates documentation from a GitHub repository URL. Accepts JSON with `repo_url` and `style_guide`. Returns JSON with documentation, success status, repository URL, and metrics.
- **`POST /download-documentation`:** Downloads the generated documentation as a Markdown file. Accepts JSON with `documentation`. Returns JSON with documentation and filename.
- **`POST /chatbot`:** Provides chatbot functionality. Accepts JSON with `question` and `documentation`. Returns JSON with the chatbot's answer.

Detailed API documentation for each endpoint is available within the comments of the respective functions in `enhanced_app.py`.

## 🤝 Contributing Guidelines

Contributions are welcome! Please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write clear and concise commit messages.
4. Ensure your code adheres to PEP 8 style guide (for Python).
5. Write unit tests for your code changes.
6. Submit a pull request with a detailed description of your changes.

Testing is crucial. Unit tests should be added to ensure the correctness of any code changes. The project should aim for high test coverage.