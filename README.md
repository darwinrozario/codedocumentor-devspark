```html

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Auto-Documenter Project Documentation</title>
<style>

body { font-family: sans-serif; }
pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
code { background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
ul { list-style-type: disc; padding-left: 20px; }

</style>
</head>
<body>
# Code Auto-Documenter Project Documentation

## 📋 Project Overview

The Code Auto-Documenter is a web application designed to automatically generate comprehensive documentation for software projects.  It leverages the Google Gemini API to analyze code and produce well-structured HTML documentation. The project aims to streamline the documentation process, improving code maintainability and collaboration.

### Technology Stack and Architecture

The project uses the following technologies:

<ul>
- **Backend:** Flask (Python)</li>
<li>**Frontend:** HTML, CSS, JavaScript</li>
<li>**AI Engine:** Google Gemini API</li>
<li>**Code Analysis:**  Abstract Syntax Tree (AST) parsing (Python)

</ul>
The architecture is a client-server model. The frontend handles user interaction (file uploads, GitHub repository input, documentation display, and chatbot interaction). The backend processes file uploads, clones GitHub repositories, analyzes code using AST parsing, calls the Gemini API for documentation generation, and handles API responses. The Gemini API is responsible for natural language processing and documentation generation.

### Project Structure and Organization

The project is organized as follows:

<ul>
- `app.py`: The initial Flask application (basic functionality).</li>
<li>`enhanced_app.py`: The enhanced Flask application with improved code analysis and features.</li>
<li>`config.yaml`: Configuration file for various settings (style guides, output formats, API keys, etc.).</li>
<li>`static/css/styles.css`: Stylesheet for the web application.</li>
<li>`static/js/script.js`: Main JavaScript file for frontend logic.</li>
<li>`static/js/chatbot.js`: JavaScript file for chatbot functionality.</li>
<li>`templates/index.html`: Main HTML template for the web application.</li>
<li>`CHATBOT_FEATURE.md`: Documentation for the chatbot feature.</li>
<li>`README.md`: Project README file.

</ul>
## 📚 File Documentation

### 📄 app.py

#### Purpose and Overview

This file contains the initial implementation of the Flask web application. It provides basic functionality for uploading code files, generating documentation using the Gemini API, and handling user requests.  It lacks the advanced code analysis features present in `enhanced_app.py`.

#### Key Functions/Classes

<ul>
- `allowed_file(filename)`: Checks if the file extension is supported.</li>
<li>`should_ignore_path(path)`: Checks if a path should be ignored (e.g., .git, node_modules).</li>
<li>`clone_github_repository(repo_url)`: Clones a GitHub repository and extracts file contents.</li>
<li>`extract_files_from_zip(zip_file)`: Extracts files from a ZIP archive.</li>
<li>`call_gemini_api(prompt)`: Calls the Gemini API to generate documentation.</li>
<li>`clean_markdown_to_html(text)`: Cleans up markdown formatting and converts it to HTML.</li>
<li>`create_documentation_prompt(file_contents)`: Creates the prompt for the Gemini API.

</ul>
#### Dependencies

<ul>
- Flask</li>
<li>requests</li>
<li>zipfile</li>
<li>re</li>
<li>subprocess</li>
<li>tempfile</li>
<li>shutil</li>
<li>werkzeug</li>
<li>pathlib

</ul>
#### Usage Examples

See the Flask routes (`@app.route` decorators) within the file for usage examples.  The main functionality is accessed through POST requests to `/generate-documentation` and `/analyze-github`.

#### Code Comments

The code includes comments explaining the purpose of functions and complex logic.

#### API Documentation

See inline comments within the functions for parameter, return value, and exception details.

### 📄 CHATBOT_FEATURE.md

#### Purpose and Overview

This markdown file provides documentation for the AI-powered chatbot feature added to the Code Auto-Documenter.  It describes the feature's capabilities, usage instructions, technical implementation details, and API endpoints.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples

The document outlines how to use the chatbot after generating documentation.

#### Code Comments (Not Applicable)

#### API Documentation

The document details the `POST /chatbot` API endpoint, including request and response structures.

### 📄 config.yaml

#### Purpose and Overview

This YAML file contains the configuration settings for the Code Auto-Documenter. It allows users to customize various aspects of the documentation generation process, including style guides, output formats, API keys, and analysis settings.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples (Not Applicable)

#### Code Comments (Not Applicable)

#### API Documentation (Not Applicable)

### 📄 enhanced_app.py

#### Purpose and Overview

This file contains an enhanced version of the Flask application. It builds upon `app.py` by incorporating advanced code analysis using Abstract Syntax Tree (AST) parsing. This allows for more detailed extraction of code structure information (functions, classes, imports) before generating documentation, resulting in more accurate and comprehensive output.  It also includes improved error handling and logging.

#### Key Functions/Classes

<ul>
- `CodeAnalyzer`: A class that analyzes code using AST parsing.</li>
<li>`PythonASTAnalyzer`: A class that extends `ast.NodeVisitor` for Python-specific AST analysis.</li>
<li>`clone_github_repository(repo_url)`: Clones a GitHub repository and extracts file contents with analysis data.</li>
<li>`is_supported_file(filename)`: Checks if a file has a supported extension.</li>
<li>`extract_files_from_zip(zip_file)`: Extracts files from a ZIP archive with analysis data.</li>
<li>`call_gemini_api(prompt)`: Calls the Gemini API, handling various response structures.</li>
<li>`generate_style_guide_prompt(language, style)`: Generates prompts with style guide information.</li>
<li>`create_documentation_prompt(file_contents, style_guide)`: Creates the prompt for the Gemini API with AST analysis data.</li>
<li>`clean_markdown_to_html(text)`: Cleans up markdown formatting and converts it to HTML.

</ul>
#### Dependencies

<ul>
- Flask</li>
<li>requests</li>
<li>zipfile</li>
<li>re</li>
<li>ast</li>
<li>astroid</li>
<li>subprocess</li>
<li>tempfile</li>
<li>shutil</li>
<li>pathlib</li>
<li>werkzeug</li>
<li>typing</li>
<li>yaml

</ul>
#### Usage Examples

Similar to `app.py`, the main functionality is accessed through POST requests to `/generate-documentation` and `/analyze-github`.  The `style_guide` parameter can be used to specify a documentation style (e.g., 'google', 'numpy').

#### Code Comments

The code includes extensive comments explaining the purpose of functions, classes, and complex logic.  There are also debug print statements for API responses and analysis data.

#### API Documentation

See inline comments within the functions for parameter, return value, and exception details.

### 📄 README.md

#### Purpose and Overview

A simple README file listing the team members.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples (Not Applicable)

#### Code Comments (Not Applicable)

#### API Documentation (Not Applicable)

### 📄 static/css/styles.css

#### Purpose and Overview

This CSS file provides styling for the Code Auto-Documenter web application. It includes styles for various elements, including the file upload section, progress bar, documentation content, chatbot interface, and fullscreen mode.  It also incorporates dark mode support.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples (Not Applicable)

#### Code Comments (Not Applicable)

#### API Documentation (Not Applicable)

### 📄 static/js/chatbot.js

#### Purpose and Overview

This JavaScript file implements the chatbot functionality. It handles user input, sends requests to the backend's `/chatbot` endpoint, receives and displays responses, and manages the chatbot's visibility.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples

The file is designed to be integrated into an HTML page.  It uses DOM manipulation to interact with the chatbot elements.

#### Code Comments

The code includes comments explaining the purpose of functions and the flow of execution.

#### API Documentation (Not Applicable)

### 📄 static/js/script.js

#### Purpose and Overview

This JavaScript file handles the main frontend logic of the Code Auto-Documenter. It manages file uploads, displays file lists, handles documentation generation requests, displays the generated documentation, implements copy and download functionality, and manages the fullscreen mode.

#### Key Functions/Classes (Not Applicable)

#### Dependencies (Not Applicable)

#### Usage Examples

The file is designed to be integrated into an HTML page.  It uses DOM manipulation, event listeners, and asynchronous requests to interact with the backend.

#### Code Comments

The code includes comments explaining the purpose of functions and the flow of execution.

#### API Documentation (Not Applicable)

### 📄 templates/index.html

#### Purpose and Overview

This HTML file serves as the main template for the Code Auto-Documenter web application. It defines the structure and layout of the user interface, including sections for file uploads, progress display, documentation output, and the chatbot.

#### Key Functions/Classes (Not Applicable)

#### Dependencies

<ul>
- Tailwind CSS</li>
<li>Font Awesome</li>
<li>Custom CSS (`styles.css`)</li>
<li>Custom JavaScript (`script.js` and `chatbot.js`)

</ul>
#### Usage Examples (Not Applicable)

#### Code Comments (Not Applicable)

#### API Documentation (Not Applicable)

## 🚀 Setup and Installation

**Prerequisites:**

<ul>
- Python 3.7+</li>
<li>Node.js and npm (for frontend development, optional)</li>
<li>A Google Cloud Platform (GCP) project with the Gemini API enabled and a valid API key.

</ul>
**Installation Steps:**

<ol>
- Clone the repository: `git clone <repository_url>`</li>
<li>Install Python dependencies: `pip install -r requirements.txt`</li>
<li>Set the `GEMINI_API_KEY` environment variable with your API key.</li>
<li>(Optional) Install Node.js and npm and run `npm install` to install frontend dependencies.</li>
<li>Run the Flask application: `python enhanced_app.py`

</ol>
**Configuration Requirements:**

The `config.yaml` file can be used to customize various settings.  The Gemini API key is crucial for the application to function.  Ensure that the API key is correctly configured either in the `config.yaml` file or as an environment variable.

## 💻 Usage Examples

The application can be used in two main ways:

<ol>
- **File Upload:** Upload individual code files or a zipped folder containing your project's code. The application will automatically identify supported file types and generate documentation.</li>
<li>**GitHub Repository Analysis:** Provide a GitHub repository URL, and the application will clone the repository, analyze the code, and generate documentation.

</ol>
After documentation generation, you can copy the HTML or Markdown content to your clipboard, download it as a Markdown file, or use the integrated chatbot to ask questions about the generated documentation.

## 🔧 API Reference

The main API endpoints are:

<ul>
- `POST /generate-documentation`: Generates documentation from uploaded files.</li>
<li>`POST /analyze-github`: Generates documentation from a GitHub repository URL.</li>
<li>`POST /download-documentation`: Downloads the generated documentation as a Markdown file.</li>
<li>`POST /chatbot`: Provides an AI-powered Q&A interface for the generated documentation.

</ul>
Detailed API documentation for each endpoint is available within the comments of the respective functions in `enhanced_app.py`.

## 🤝 Contributing Guidelines

Contributions are welcome! Please follow these guidelines:

<ul>
- Fork the repository.</li>
<li>Create a new branch for your feature or bug fix.</li>
<li>Write clear and concise commit messages.</li>
<li>Ensure your code adheres to the PEP 8 style guide for Python.</li>
<li>Write unit tests for your code changes.</li>
<li>Submit a pull request with a detailed description of your changes.

</ul>
Testing is crucial.  Unit tests should be added to ensure the correctness of any code changes.

</body>
</html>

```