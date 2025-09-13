from flask import Flask, render_template, request, jsonify
import os
import json
import requests
import zipfile
import io
import re
import subprocess
import tempfile
import shutil
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size for folders

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyCOFOoppNQRakvBcKyKmWHEHpMBPODi9s4"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'js', 'py', 'java', 'cpp', 'c', 'html', 'css', 'php', 
    'rb', 'go', 'rs', 'ts', 'jsx', 'tsx', 'vue', 'svelte',
    'md', 'txt', 'json', 'xml', 'yaml', 'yml', 'toml', 'ini',
    'sh', 'bat', 'ps1', 'sql', 'r', 'scala', 'kt', 'swift'
}

# Files/folders to ignore
IGNORE_PATTERNS = {
    '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
    'dist', 'build', 'target', 'bin', 'obj', 'venv', 'env',
    '.DS_Store', 'Thumbs.db', '.gitignore', '.env'
}

def allowed_file(filename):
    """Check if file extension is supported"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS

def should_ignore_path(path):
    """Check if path should be ignored"""
    path_parts = Path(path).parts
    return any(part in IGNORE_PATTERNS for part in path_parts)

def clone_github_repository(repo_url):
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
                    if not allowed_file(file):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if not content.strip():
                            continue
                        
                        file_contents.append({
                            'name': rel_path,
                            'content': content,
                            'extension': Path(file).suffix[1:].lower() if Path(file).suffix else 'txt'
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

def extract_files_from_zip(zip_file):
    """Extract and process files from uploaded ZIP folder"""
    file_contents = []
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                # Skip directories and ignored files
                if file_info.is_dir() or should_ignore_path(file_info.filename):
                    continue
                
                # Check if file extension is supported
                if not allowed_file(file_info.filename):
                    continue
                
                try:
                    # Read file content
                    with zip_ref.open(file_info.filename) as file:
                        content = file.read().decode('utf-8')
                        
                        # Skip empty files
                        if not content.strip():
                            continue
                        
                        file_contents.append({
                            'name': file_info.filename,
                            'content': content,
                            'extension': Path(file_info.filename).suffix[1:].lower() if Path(file_info.filename).suffix else 'txt'
                        })
                except UnicodeDecodeError:
                    # Skip binary files
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
                    "temperature": 0.3,
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
        return data['candidates'][0]['content']['parts'][0]['text']
    
    except Exception as e:
        raise Exception(f"Failed to generate documentation: {str(e)}")

def clean_markdown_to_html(text):
    """Convert markdown formatting to proper HTML"""
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert *text* to <em>text</em> (but not inside code blocks)
    text = re.sub(r'(?<!`)\*([^*`]+)\*(?!`)', r'<em>\1</em>', text)
    
    # Convert `code` to <code>code</code> (but not inside code blocks)
    text = re.sub(r'(?<!`)`([^`]+)`(?!`)', r'<code>\1</code>', text)
    
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

def create_documentation_prompt(file_contents):
    """Create the prompt for documentation generation"""
    if not file_contents:
        return "No valid files found to analyze."
    
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

    # Group files by directory for better organization
    files_by_dir = {}
    for file_data in file_contents:
        dir_path = str(Path(file_data['name']).parent)
        if dir_path == '.':
            dir_path = 'Root'
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(file_data)
    
    # Add files to prompt, organized by directory
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
</ul>

<h1>📚 File Documentation</h1>
<p>Individual file analysis (as requested above)</p>

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
<li>Code examples</li>
</ul>

<h1>🔧 API Reference</h1>
<ul>
<li>Function and class documentation</li>
<li>Parameter descriptions</li>
<li>Return value explanations</li>
<li>Error handling</li>
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
        prompt = create_documentation_prompt(file_contents)
        documentation = call_gemini_api(prompt)
        
        # Clean up any remaining markdown formatting
        documentation = clean_markdown_to_html(documentation)
        
        return jsonify({
            'success': True,
            'documentation': documentation,
            'files_processed': len(file_contents)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-github', methods=['POST'])
def analyze_github():
    """API endpoint to analyze GitHub repository"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url', '').strip()
        
        if not repo_url:
            return jsonify({'error': 'No repository URL provided'}), 400
        
        # Clone and analyze the repository
        file_contents = clone_github_repository(repo_url)
        
        if not file_contents:
            return jsonify({'error': 'No valid code files found in the repository.'}), 400
        
        # Generate documentation
        prompt = create_documentation_prompt(file_contents)
        documentation = call_gemini_api(prompt)
        
        # Clean up any remaining markdown formatting
        documentation = clean_markdown_to_html(documentation)
        
        return jsonify({
            'success': True,
            'documentation': documentation,
            'files_processed': len(file_contents),
            'repo_url': repo_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 