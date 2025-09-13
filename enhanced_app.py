from flask import Flask, render_template, request, jsonify
import os
import json
import requests
import zipfile
import io
import re
import ast
import astroid
import subprocess
import tempfile
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
from typing import Dict, List, Any, Optional
import yaml

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAGFn61sg4_mCncJDTeMFF8-t-4oUEUCvk"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Supported file extensions with language mapping
LANGUAGE_EXTENSIONS = {
    'python': {'py', 'pyi'},
    'javascript': {'js', 'jsx'},
    'typescript': {'ts', 'tsx'},
    'java': {'java'},
    'cpp': {'cpp', 'cc', 'cxx', 'h', 'hpp'},
    'c': {'c'},
    'go': {'go'},
    'rust': {'rs'},
    'php': {'php'},
    'ruby': {'rb'},
    'swift': {'swift'},
    'kotlin': {'kt'},
    'scala': {'scala'},
    'r': {'r'},
    'sql': {'sql'},
    'html': {'html', 'htm'},
    'css': {'css', 'scss', 'sass'},
    'vue': {'vue'},
    'svelte': {'svelte'},
    'markdown': {'md', 'mdx'},
    'yaml': {'yaml', 'yml'},
    'json': {'json'},
    'xml': {'xml'},
    'toml': {'toml'},
    'ini': {'ini', 'cfg'},
    'shell': {'sh', 'bash', 'zsh'},
    'batch': {'bat', 'cmd'},
    'powershell': {'ps1'}
}

# Simple supported extensions set for compatibility with app.py
SUPPORTED_EXTENSIONS = {
    'js', 'py', 'java', 'cpp', 'c', 'html', 'css', 'php', 
    'rb', 'go', 'rs', 'ts', 'jsx', 'tsx', 'vue', 'svelte',
    'md', 'txt', 'json', 'xml', 'yaml', 'yml', 'toml', 'ini',
    'sh', 'bat', 'ps1', 'sql', 'r', 'scala', 'kt', 'swift'
}

# Style guides for different languages
STYLE_GUIDES = {
    'python': {
        'google': 'Google Python Style G  uide',
        'numpy': 'NumPy Docstring Convention',
        'sphinx': 'Sphinx Documentation Style'
    },
    'javascript': {
        'jsdoc': 'JSDoc Style Guide',
        'google': 'Google JavaScript Style Guide'
    },
    'typescript': {
        'typedoc': 'TypeDoc Style Guide',
        'jsdoc': 'JSDoc Style Guide'
    },
    'java': {
        'javadoc': 'JavaDoc Style Guide',
        'google': 'Google Java Style Guide'
    }
}

# Files/folders to ignore
IGNORE_PATTERNS = {
    '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
    'dist', 'build', 'target', 'bin', 'obj', 'venv', 'env',
    '.DS_Store', 'Thumbs.db', '.gitignore', '.env', '*.pyc',
    '*.class', '*.o', '*.so', '*.dll', '*.exe'
}

def clone_github_repository(repo_url: str) -> List[Dict[str, Any]]:
    """Clone a GitHub repository and return file contents"""
    try:
        # Validate GitHub URL
        if not repo_url.startswith('https://github.com/'):
            raise Exception("Invalid GitHub URL. Please use https://github.com/username/repository format")
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone the repository
            result = subprocess.run(
                ['git', 'clone', repo_url, temp_dir],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            # Extract files from the cloned repository
            file_contents = []
            
            for root, dirs, files in os.walk(temp_dir):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)
                    
                    # Check if file is supported
                    if not is_supported_file(file):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if not content.strip():
                            continue
                        
                        # Analyze the file
                        analyzer = CodeAnalyzer()
                        if file.endswith('.py'):
                            analysis = analyzer.analyze_python_file(rel_path, content)
                        elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                            analysis = analyzer.analyze_javascript_file(rel_path, content)
                        else:
                            analysis = {
                                'language': 'unknown',
                                'file_path': rel_path,
                                'line_count': len(content.splitlines())
                            }
                        
                        file_contents.append({
                            'name': rel_path,
                            'content': content,
                            'extension': Path(file).suffix[1:].lower() if Path(file).suffix else 'txt',
                            'analysis': analysis
                        })
                        
                    except Exception as e:
                        print(f"Error reading file {rel_path}: {e}")
                        continue
            
            return file_contents
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except subprocess.TimeoutExpired:
        raise Exception("Repository cloning timed out. Please try with a smaller repository or check your internet connection.")
    except Exception as e:
        raise Exception(f"Error processing GitHub repository: {str(e)}")

def is_supported_file(filename: str) -> bool:
    """Check if file is supported"""
    ext = Path(filename).suffix[1:].lower()
    # Check both the simple set and the language extensions
    return ext in SUPPORTED_EXTENSIONS or any(ext in exts for exts in LANGUAGE_EXTENSIONS.values())

class CodeAnalyzer:
    """Analyzes code structure using AST parsing"""
    
    def __init__(self):
        self.symbols = {}
        self.dependencies = {}
        self.call_graph = {}
    
    def analyze_python_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        try:
            tree = ast.parse(content)
            analyzer = PythonASTAnalyzer()
            analyzer.visit(tree)
            return {
                'language': 'python',
                'file_path': file_path,
                'symbols': analyzer.symbols,
                'imports': analyzer.imports,
                'classes': analyzer.classes,
                'functions': analyzer.functions,
                'line_count': len(content.splitlines())
            }
        except Exception as e:
            return {
                'language': 'python',
                'file_path': file_path,
                'error': str(e),
                'line_count': len(content.splitlines())
            }
    
    def analyze_javascript_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file"""
        try:
            # Basic regex-based analysis for JS/TS
            function_names = re.findall(r'function\s+(\w+)\s*\([^)]*\)', content)
            class_names = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            
            # Convert function names to proper function objects
            functions = []
            for func_name in function_names:
                functions.append({
                    'name': func_name,
                    'args': [],  # We can't easily extract args with regex
                    'returns': None,
                    'line_number': 0,  # We can't easily get line numbers with regex
                    'docstring': None,
                    'class': None
                })
            
            # Convert class names to proper class objects
            classes = []
            for class_name in class_names:
                classes.append({
                    'name': class_name,
                    'bases': [],
                    'methods': [],
                    'line_number': 0,
                    'docstring': None
                })
            
            return {
                'language': 'javascript' if file_path.endswith(('.js', '.jsx')) else 'typescript',
                'file_path': file_path,
                'symbols': {'functions': function_names, 'classes': class_names},
                'imports': imports,
                'classes': classes,
                'functions': functions,
                'line_count': len(content.splitlines())
            }
        except Exception as e:
            return {
                'language': 'javascript',
                'file_path': file_path,
                'error': str(e),
                'line_count': len(content.splitlines())
            }

class PythonASTAnalyzer(ast.NodeVisitor):
    """AST visitor for Python code analysis"""
    
    def __init__(self):
        self.symbols = {}
        self.imports = []
        self.classes = []
        self.functions = []
        self.current_class = None
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        module = node.module or ''
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        class_info = {
            'name': node.name,
            'bases': [self._get_name(base) for base in node.bases],
            'methods': [],
            'line_number': node.lineno,
            'docstring': ast.get_docstring(node)
        }
        
        self.current_class = node.name
        self.classes.append(class_info)
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        func_info = {
            'name': node.name,
            'args': self._get_function_args(node.args),
            'returns': self._get_annotation(node.returns),
            'line_number': node.lineno,
            'docstring': ast.get_docstring(node),
            'class': self.current_class
        }
        
        self.functions.append(func_info)
        if self.current_class:
            # Add to class methods
            for cls in self.classes:
                if cls['name'] == self.current_class:
                    cls['methods'].append(func_info)
                    break
        
        self.generic_visit(node)
    
    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _get_function_args(self, args):
        params = []
        for arg in args.args:
            param = {
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation)
            }
            params.append(param)
        return params
    
    def _get_annotation(self, node):
        if node is None:
            return None
        return self._get_name(node)

def allowed_file(filename):
    """Check if file extension is supported"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    # Check both the simple set and the language extensions
    return ext in SUPPORTED_EXTENSIONS or any(ext in exts for exts in LANGUAGE_EXTENSIONS.values())

def should_ignore_path(path):
    """Check if path should be ignored"""
    path_parts = Path(path).parts
    return any(part in IGNORE_PATTERNS for part in path_parts)

def extract_files_from_zip(zip_file):
    """Extract and process files from uploaded ZIP folder"""
    file_contents = []
    analyzer = CodeAnalyzer()
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.is_dir() or should_ignore_path(file_info.filename):
                    continue
                
                if not allowed_file(file_info.filename):
                    continue
                
                try:
                    with zip_ref.open(file_info.filename) as file:
                        content = file.read().decode('utf-8')
                        
                        if not content.strip():
                            continue
                        
                        # Analyze the file (optional for compatibility)
                        try:
                            if file_info.filename.endswith('.py'):
                                analysis = analyzer.analyze_python_file(file_info.filename, content)
                            elif file_info.filename.endswith(('.js', '.jsx', '.ts', '.tsx')):
                                analysis = analyzer.analyze_javascript_file(file_info.filename, content)
                            else:
                                analysis = {
                                    'language': 'unknown',
                                    'file_path': file_info.filename,
                                    'line_count': len(content.splitlines())
                                }
                        except Exception as e:
                            # Fallback to simple analysis if AST parsing fails
                            analysis = {
                                'language': 'unknown',
                                'file_path': file_info.filename,
                                'line_count': len(content.splitlines())
                            }
                        
                        file_contents.append({
                            'name': file_info.filename,
                            'content': content,
                            'extension': Path(file_info.filename).suffix[1:].lower() if Path(file_info.filename).suffix else 'txt',
                            'analysis': analysis
                        })
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error reading file {file_info.filename}: {e}")
                    continue
    
    except Exception as e:
        raise Exception(f"Error processing ZIP file: {str(e)}")
    
    return file_contents

def call_gemini_api(prompt):
    """Call Gemini API to generate documentation"""
    try:
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 32,
                    "topP": 0.95,
                    "maxOutputTokens": 16384
                }
            },
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} {response.text}")
        
        data = response.json()
        
        # Debug: Print the response structure
        print(f"API Response structure: {type(data)}")
        print(f"API Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        
        # Handle different response structures
        if 'candidates' in data and len(data['candidates']) > 0:
            candidate = data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                return candidate['content']['parts'][0]['text']
            else:
                raise Exception(f"Unexpected candidate structure: {candidate}")
        elif 'error' in data:
            raise Exception(f"API Error: {data['error']}")
        else:
            # Try alternative response structure
            if 'text' in data:
                return data['text']
            elif 'response' in data:
                return data['response']
            else:
                raise Exception(f"Unexpected API response structure: {data}")
    
    except Exception as e:
        print(f"API Error details: {str(e)}")
        raise Exception(f"Failed to generate documentation: {str(e)}")

def generate_style_guide_prompt(language: str, style: str) -> str:
    """Generate style guide specific prompt"""
    style_guides = {
        'python': {
            'google': """
Use Google Python Style Guide for docstrings:
- Use triple quotes for docstrings
- Include Args, Returns, Raises sections
- Example:
def function_name(param1: str, param2: int) -> bool:
    \"\"\"Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: Description of when this error occurs.
    \"\"\"
""",
            'numpy': """
Use NumPy Docstring Convention:
- Use triple quotes for docstrings
- Include Parameters, Returns, Raises sections
- Example:
def function_name(param1, param2):
    \"\"\"
    Short description.
    
    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int
        Description of param2.
    
    Returns
    -------
    bool
        Description of return value.
    
    Raises
    ------
    ValueError
        Description of when this error occurs.
    \"\"\"
"""
        },
        'javascript': {
            'jsdoc': """
Use JSDoc Style Guide:
- Use /** */ for docstrings
- Include @param, @returns, @throws tags
- Example:
/**
 * Short description.
 * 
 * @param {string} param1 - Description of param1.
 * @param {number} param2 - Description of param2.
 * @returns {boolean} Description of return value.
 * @throws {Error} Description of when this error occurs.
 */
function functionName(param1, param2) {
"""
        }
    }
    
    return style_guides.get(language, {}).get(style, "")

def create_documentation_prompt(file_contents, style_guide='google'):
    """Create the prompt for documentation generation with AST analysis"""
    if not file_contents:
        return "No valid files found to analyze."
    
    # Check if files have analysis data (enhanced format) or simple format
    has_analysis = any('analysis' in file_data for file_data in file_contents)
    
    if has_analysis:
        # Group files by language (enhanced format)
        files_by_language = {}
        for file_data in file_contents:
            lang = file_data.get('analysis', {}).get('language', 'unknown')
            if lang not in files_by_language:
                files_by_language[lang] = []
            files_by_language[lang].append(file_data)
    else:
        # Group files by directory (simple format from app.py)
        files_by_dir = {}
        for file_data in file_contents:
            dir_path = str(Path(file_data['name']).parent)
            if dir_path == '.':
                dir_path = 'Root'
            if dir_path not in files_by_dir:
                files_by_dir[dir_path] = []
            files_by_dir[dir_path].append(file_data)
    
    if has_analysis:
        prompt = f"""Please analyze the following code files and generate comprehensive, well-structured documentation using HTML formatting (NOT markdown).

The code has been analyzed using AST parsing to extract symbols, functions, classes, and dependencies. Use this information to create accurate documentation.

For each file, provide:

1. <strong>Purpose and Overview</strong>: What the file does and its role in the project
2. <strong>Key Functions/Classes</strong>: Main components with their purpose and functionality
3. <strong>Dependencies</strong>: External libraries, modules, or frameworks used
4. <strong>Usage Examples</strong>: How to use key functions/classes with code examples
5. <strong>Code Comments</strong>: Explain complex logic, algorithms, and important decisions
6. <strong>API Documentation</strong>: For functions, include parameters, return values, and exceptions

Format the output in clean, professional HTML with:
- Clear hierarchical headings (<h1>, <h2>, <h3>, <h4>)
- Proper code blocks with syntax highlighting
- Bold text for emphasis using <strong>text</strong> (NOT **text**)
- Italic text using <em>text</em> (NOT *text*)
- Clean spacing and organization
- Tables where appropriate using <table>, <tr>, <th>, <td>
- Lists using <ul> and <li> for better readability
- Paragraphs wrapped in <p> tags

{generate_style_guide_prompt('python', style_guide)}

Here are the analyzed code files:

---

"""
    else:
        prompt = """Please analyze the following code files and generate comprehensive, well-structured documentation using HTML formatting (NOT markdown).

For each file, provide:

1. <strong>Purpose and Overview</strong>: What the file does and its role in the project
2. <strong>Key Functions/Classes</strong>: Main components with their purpose and functionality
3. <strong>Dependencies</strong>: External libraries, modules, or frameworks used
4. <strong>Usage Examples</strong>: How to use key functions/classes with code examples
5. <strong>Code Comments</strong>: Explain complex logic, algorithms, and important decisions
6. <strong>API Documentation</strong>: For functions, include parameters, return values, and exceptions

Format the output in clean, professional HTML with:
- Clear hierarchical headings (<h1>, <h2>, <h3>, <h4>)
- Proper code blocks with syntax highlighting
- Bold text for emphasis using <strong>text</strong> (NOT **text**)
- Italic text using <em>text</em> (NOT *text*)
- Clean spacing and organization
- Tables where appropriate using <table>, <tr>, <th>, <td>
- Lists using <ul> and <li> for better readability
- Paragraphs wrapped in <p> tags

Here are the code files to analyze:

---

"""

    if has_analysis:
        # Add files to prompt, organized by language
        for language, files in files_by_language.items():
            prompt += f"<h2>🔧 {language.upper()} Files</h2>\n\n"
            
            for file_data in files:
                analysis = file_data['analysis']
                prompt += f"<h3>📄 {file_data['name']}</h3>\n\n"
                prompt += f"<strong>File Type</strong>: {file_data['extension'].upper()}\n"
                prompt += f"<strong>Lines of Code</strong>: {analysis.get('line_count', 'Unknown')}\n\n"
            
            # Debug: Print analysis structure
            print(f"Analysis for {file_data['name']}: {type(analysis)}")
            if 'functions' in analysis:
                print(f"Functions type: {type(analysis['functions'])}, length: {len(analysis['functions']) if isinstance(analysis['functions'], list) else 'not a list'}")
                if analysis['functions'] and len(analysis['functions']) > 0:
                    print(f"First function: {type(analysis['functions'][0])} = {analysis['functions'][0]}")
            
            # Add analysis information
            if 'functions' in analysis and analysis['functions']:
                prompt += f"<strong>Functions Found</strong>: {len(analysis['functions'])}\n"
                for func in analysis['functions'][:5]:  # Show first 5 functions
                    try:
                        # Handle both string and dict function representations
                        if isinstance(func, str):
                            prompt += f"- {func}()\n"
                        elif isinstance(func, dict):
                            args = func.get('args', [])
                            if isinstance(args, list):
                                arg_names = [arg.get('name', 'unknown') if isinstance(arg, dict) else str(arg) for arg in args]
                            else:
                                arg_names = [str(args)]
                            prompt += f"- {func.get('name', 'unknown')}({', '.join(arg_names)})\n"
                        else:
                            prompt += f"- {str(func)}()\n"
                    except Exception as e:
                        print(f"Error processing function {func}: {e}")
                        if isinstance(func, str):
                            prompt += f"- {func}()\n"
                        else:
                            prompt += f"- unknown_function()\n"
                prompt += "\n"
            
            if 'classes' in analysis and analysis['classes']:
                prompt += f"<strong>Classes Found</strong>: {len(analysis['classes'])}\n"
                for cls in analysis['classes'][:3]:  # Show first 3 classes
                    try:
                        # Handle both string and dict class representations
                        if isinstance(cls, str):
                            prompt += f"- {cls}\n"
                        elif isinstance(cls, dict):
                            prompt += f"- {cls.get('name', 'unknown')}\n"
                        else:
                            prompt += f"- {str(cls)}\n"
                    except Exception as e:
                        print(f"Error processing class {cls}: {e}")
                        if isinstance(cls, str):
                            prompt += f"- {cls}\n"
                        else:
                            prompt += f"- unknown_class\n"
                prompt += "\n"
            
            if 'imports' in analysis and analysis['imports']:
                try:
                    imports = analysis['imports']
                    if isinstance(imports, list):
                        import_list = imports[:10]
                    else:
                        import_list = [str(imports)]
                    prompt += f"<strong>Dependencies</strong>: {', '.join(import_list)}\n\n"
                except Exception as e:
                    print(f"Error processing imports: {e}")
                    prompt += f"<strong>Dependencies</strong>: unknown\n\n"
            
                prompt += f"<pre><code class=\"{file_data['extension']}\">{file_data['content']}</code></pre>\n\n---\n\n"
    else:
        # Add files to prompt, organized by directory (simple format)
        for dir_path, files in sorted(files_by_dir.items()):
            if dir_path != 'Root':
                prompt += f"<h2>📁 {dir_path}/</h2>\n\n"
            
            for file_data in files:
                prompt += f"<h3>📄 {file_data['name']}</h3>\n\n"
                prompt += f"<strong>File Type</strong>: {file_data['extension'].upper()}\n\n"
                prompt += f"<pre><code class=\"{file_data['extension']}\">{file_data['content']}</code></pre>\n\n---\n\n"

    prompt += """

Please provide a comprehensive project documentation that includes:

<h1>📋 Project Overview</h1>
<ul>
<li>Project purpose and goals</li>
<li>Technology stack and architecture</li>
<li>Project structure and organization</li>
<li>Dependency analysis and call graph summary</li>
</ul>

<h1>📚 File Documentation</h1>
<p>Individual file analysis with AST-extracted information</p>

<h1>🚀 Setup and Installation</h1>
<ul>
<li>Prerequisites and dependencies</li>
<li>Installation steps</li>
<li>Configuration requirements</li>
</ul>

<h1>💻 Usage Examples</h1>
<ul>
<li>How to run the project</li>
<li>Common use cases</li>
<li>Code examples with proper docstrings</li>
</ul>

<h1>🔧 API Reference</h1>
<ul>
<li>Function and class documentation with parameters</li>
<li>Return value explanations</li>
<li>Error handling and exceptions</li>
<li>Type information where available</li>
</ul>

<h1>🤝 Contributing Guidelines</h1>
<ul>
<li>How to contribute to the project</li>
<li>Code style and standards</li>
<li>Testing requirements</li>
</ul>

Make the documentation clear, professional, and useful for developers who want to understand and work with this codebase. Use proper HTML formatting with <strong>bold text</strong>, <em>italic text</em>, and clear organization. DO NOT use markdown syntax like **text** or *text*."""

    return prompt

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/generate-documentation', methods=['POST'])
def generate_documentation():
    """API endpoint to generate documentation from uploaded files or folders"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        style_guide = request.form.get('style_guide', 'google')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        file_contents = []
        
        for file in files:
            if not file:
                continue
                
            filename = secure_filename(file.filename)
            
            # Check if it's a ZIP file (folder upload)
            if filename.lower().endswith('.zip'):
                try:
                    zip_contents = extract_files_from_zip(file)
                    file_contents.extend(zip_contents)
                except Exception as e:
                    return jsonify({'error': f'Error processing ZIP file: {str(e)}'}), 400
            else:
                # Single file upload
                if allowed_file(filename):
                    try:
                        content = file.read().decode('utf-8')
                        if content.strip():  # Skip empty files
                            # Try enhanced analysis first, fallback to simple format
                            try:
                                analyzer = CodeAnalyzer()
                                if filename.endswith('.py'):
                                    analysis = analyzer.analyze_python_file(filename, content)
                                elif filename.endswith(('.js', '.jsx', '.ts', '.tsx')):
                                    analysis = analyzer.analyze_javascript_file(filename, content)
                                else:
                                    analysis = {
                                        'language': 'unknown',
                                        'file_path': filename,
                                        'line_count': len(content.splitlines())
                                    }
                                
                                file_contents.append({
                                    'name': filename,
                                    'content': content,
                                    'extension': filename.rsplit('.', 1)[1].lower(),
                                    'analysis': analysis
                                })
                            except Exception as e:
                                # Fallback to simple format (compatible with app.py)
                                file_contents.append({
                                    'name': filename,
                                    'content': content,
                                    'extension': filename.rsplit('.', 1)[1].lower()
                                })
                    except UnicodeDecodeError:
                        return jsonify({'error': f'Cannot read file {filename}. Please ensure it\'s a text file.'}), 400
        
        if not file_contents:
            return jsonify({'error': 'No valid code files found in the uploaded content.'}), 400
        
        # Generate documentation
        try:
            print(f"Creating documentation prompt for {len(file_contents)} files...")
            prompt = create_documentation_prompt(file_contents, style_guide)
            print(f"Prompt created successfully, length: {len(prompt)}")
            
            print("Calling Gemini API...")
            documentation = call_gemini_api(prompt)
            print(f"API call successful, documentation length: {len(documentation)}")
            
            # Clean up any remaining markdown formatting
            print("Cleaning markdown formatting...")
            documentation = clean_markdown_to_html(documentation)
            print("Markdown cleaning completed")
        except Exception as e:
            print(f"Error in documentation generation: {str(e)}")
            raise e
        
        # Calculate metrics (handle both enhanced and simple formats)
        total_lines = 0
        total_functions = 0
        total_classes = 0
        languages = set()
        
        for fc in file_contents:
            if 'analysis' in fc:
                # Enhanced format
                analysis = fc['analysis']
                total_lines += analysis.get('line_count', 0)
                total_functions += len(analysis.get('functions', []))
                total_classes += len(analysis.get('classes', []))
                languages.add(analysis.get('language', 'unknown'))
            else:
                # Simple format - basic line count
                total_lines += len(fc['content'].splitlines())
                languages.add('unknown')
        
        return jsonify({
            'success': True,
            'documentation': documentation,
            'files_processed': len(file_contents),
            'metrics': {
                'total_lines': total_lines,
                'total_functions': total_functions,
                'total_classes': total_classes,
                'languages': list(languages)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-github', methods=['POST'])
def analyze_github():
    """API endpoint to analyze GitHub repository"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url', '').strip()
        style_guide = data.get('style_guide', 'google')
        
        if not repo_url:
            return jsonify({'error': 'No repository URL provided'}), 400
        
        # Clone and analyze the repository
        file_contents = clone_github_repository(repo_url)
        
        if not file_contents:
            return jsonify({'error': 'No valid code files found in the repository.'}), 400
        
        # Generate documentation
        try:
            print(f"Creating documentation prompt for {len(file_contents)} files from GitHub repo...")
            prompt = create_documentation_prompt(file_contents, style_guide)
            print(f"Prompt created successfully, length: {len(prompt)}")
            
            print("Calling Gemini API...")
            documentation = call_gemini_api(prompt)
            print(f"API call successful, documentation length: {len(documentation)}")
            
            # Clean up any remaining markdown formatting
            print("Cleaning markdown formatting...")
            documentation = clean_markdown_to_html(documentation)
            print("Markdown cleaning completed")
        except Exception as e:
            print(f"Error in documentation generation: {str(e)}")
            raise e
        
        # Calculate metrics (handle both enhanced and simple formats)
        total_lines = 0
        total_functions = 0
        total_classes = 0
        languages = set()
        
        for fc in file_contents:
            if 'analysis' in fc:
                # Enhanced format
                analysis = fc['analysis']
                total_lines += analysis.get('line_count', 0)
                total_functions += len(analysis.get('functions', []))
                total_classes += len(analysis.get('classes', []))
                languages.add(analysis.get('language', 'unknown'))
            else:
                # Simple format - basic line count
                total_lines += len(fc['content'].splitlines())
                languages.add('unknown')
        
        return jsonify({
            'success': True,
            'documentation': documentation,
            'files_processed': len(file_contents),
            'repo_url': repo_url,
            'metrics': {
                'total_lines': total_lines,
                'total_functions': total_functions,
                'total_classes': total_classes,
                'languages': list(languages)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def clean_markdown_to_html(text):
    """Convert markdown formatting to proper HTML"""
    # Convert **text** to <strong>text</strong> (handle multiple occurrences)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
    
    # Convert *text* to <em>text</em> (but not inside code blocks)
    text = re.sub(r'(?<!`)\*([^*`]+)\*(?!`)', r'<em>\1</em>', text)
    
    # Convert `code` to <code>code</code> (but not inside code blocks)
    text = re.sub(r'(?<!`)`([^`]+)`(?!`)', r'<code>\1</code>', text)
    
    # Additional cleanup for common markdown patterns
    # Convert ### headings to proper HTML
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Convert - list items to <li>
    text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Wrap consecutive <li> elements in <ul>
    lines = text.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('<li>'):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(line)
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    text = '\n'.join(result_lines)
    
    # Convert paragraphs (non-empty lines that aren't HTML tags)
    lines = text.split('\n')
    result_lines = []
    in_paragraph = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_paragraph:
                result_lines.append('</p>')
                in_paragraph = False
        elif line.startswith('<') and line.endswith('>'):
            # HTML tag, close paragraph if open
            if in_paragraph:
                result_lines.append('</p>')
                in_paragraph = False
            result_lines.append(line)
        else:
            # Regular text, start paragraph if not already in one
            if not in_paragraph:
                result_lines.append('<p>')
                in_paragraph = True
            result_lines.append(line)
    
    if in_paragraph:
        result_lines.append('</p>')
    
    text = '\n'.join(result_lines)
    
    return text

@app.route('/download-documentation', methods=['POST'])
def download_documentation():
    """API endpoint to download documentation as markdown file"""
    try:
        data = request.get_json()
        documentation = data.get('documentation', '')
        
        if not documentation:
            return jsonify({'error': 'No documentation provided'}), 400
        
        return jsonify({
            'success': True,
            'documentation': documentation,
            'filename': 'project-documentation.md'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """API endpoint for chatbot functionality"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        documentation = data.get('documentation', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if not documentation:
            return jsonify({'error': 'No documentation context provided'}), 400
        
        # Create a prompt for the chatbot
        chatbot_prompt = f"""
You are an AI assistant helping developers understand their code project. Based on the following project documentation, please answer the user's question in a CONCISE and helpful way.

Project Documentation:
{documentation}

User Question: {question}

IMPORTANT INSTRUCTIONS:
1. Keep your response SHORT and FOCUSED (maximum 3-4 sentences)
2. Answer directly what the user asked
3. If referencing code, mention specific function/class names
4. Use HTML formatting: <strong>bold text</strong> and <em>italic text</em> (NOT markdown **text** or *text*)
5. If the question is about usage, provide a brief example
6. If troubleshooting, give a concise solution
7. Be conversational but professional

Format your response in clean HTML with proper tags like <p>, <strong>, <em>, <code>, <ul>, <li>.
"""
        
        # Call Gemini API for chatbot response
        response = call_gemini_api(chatbot_prompt)
        
        # Clean up any remaining markdown formatting in the response
        response = clean_markdown_to_html(response)
        
        return jsonify({
            'success': True,
            'answer': response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
