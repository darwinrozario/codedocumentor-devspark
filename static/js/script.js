// Dark mode setup
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark');
}
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    if (event.matches) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
});

// Global variables
let selectedFiles = [];
let generatedDocumentation = '';

// Make generatedDocumentation globally accessible and create a setter
window.generatedDocumentation = generatedDocumentation;

// Function to update global documentation variable
function updateGlobalDocumentation(doc) {
    generatedDocumentation = doc;
    window.generatedDocumentation = doc;
}

// Initialize chatbot state when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Disable chatbot initially since no documentation is available yet
    if (typeof window.disableChatbot === 'function') {
        window.disableChatbot();
    }
});

// HTML to Markdown converter function
function htmlToMarkdown(html) {
    // Create a temporary div to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Function to process text nodes and convert HTML to Markdown
    function processNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            return node.textContent;
        }
        
        if (node.nodeType !== Node.ELEMENT_NODE) {
            return '';
        }
        
        const tagName = node.tagName.toLowerCase();
        let content = '';
        
        // Process child nodes
        for (let child of node.childNodes) {
            content += processNode(child);
        }
        
        // Convert HTML tags to Markdown
        switch (tagName) {
            case 'h1':
                return `# ${content}\n\n`;
            case 'h2':
                return `## ${content}\n\n`;
            case 'h3':
                return `### ${content}\n\n`;
            case 'h4':
                return `#### ${content}\n\n`;
            case 'h5':
                return `##### ${content}\n\n`;
            case 'h6':
                return `###### ${content}\n\n`;
            case 'p':
                return `${content}\n\n`;
            case 'strong':
            case 'b':
                return `**${content}**`;
            case 'em':
            case 'i':
                return `*${content}*`;
            case 'code':
                // Check if this is inline code (not in a pre block)
                if (node.parentElement && node.parentElement.tagName.toLowerCase() === 'pre') {
                    return content;
                }
                return `\`${content}\``;
            case 'pre':
                // Extract language from class if available
                const codeElement = node.querySelector('code');
                let language = '';
                if (codeElement && codeElement.className) {
                    const langMatch = codeElement.className.match(/language-(\w+)/);
                    if (langMatch) {
                        language = langMatch[1];
                    } else {
                        // Try to extract from class name directly
                        const classes = codeElement.className.split(' ');
                        for (let cls of classes) {
                            if (cls && cls !== 'syntax-highlighted') {
                                language = cls;
                                break;
                            }
                        }
                    }
                }
                return `\`\`\`${language}\n${content}\n\`\`\`\n\n`;
            case 'ul':
                return `${content}\n`;
            case 'ol':
                return `${content}\n`;
            case 'li':
                // Check if parent is ol or ul
                const parent = node.parentElement;
                if (parent && parent.tagName.toLowerCase() === 'ol') {
                    // For ordered lists, we'll use 1. for simplicity
                    return `1. ${content}\n`;
                } else {
                    return `- ${content}\n`;
                }
            case 'blockquote':
                return `> ${content}\n\n`;
            case 'table':
                return convertTableToMarkdown(node);
            case 'br':
                return '\n';
            case 'hr':
                return '\n---\n\n';
            case 'a':
                const href = node.getAttribute('href');
                if (href) {
                    return `[${content}](${href})`;
                }
                return content;
            case 'img':
                const src = node.getAttribute('src');
                const alt = node.getAttribute('alt') || '';
                if (src) {
                    return `![${alt}](${src})`;
                }
                return '';
            case 'div':
            case 'span':
                // Just return content for div and span
                return content;
            default:
                // For unknown tags, just return the content
                return content;
        }
    }
    
    // Helper function to convert HTML table to Markdown
    function convertTableToMarkdown(tableNode) {
        let markdown = '\n';
        const rows = tableNode.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.querySelectorAll('th, td');
            let rowMarkdown = '|';
            
            for (let cell of cells) {
                rowMarkdown += ` ${processNode(cell).trim()} |`;
            }
            
            markdown += rowMarkdown + '\n';
            
            // Add header separator after first row if it contains th elements
            if (i === 0 && row.querySelectorAll('th').length > 0) {
                let separator = '|';
                for (let j = 0; j < cells.length; j++) {
                    separator += ' --- |';
                }
                markdown += separator + '\n';
            }
        }
        
        return markdown + '\n';
    }
    
    // Process the entire HTML
    let markdown = '';
    for (let child of tempDiv.childNodes) {
        markdown += processNode(child);
    }
    
    // Clean up extra newlines
    markdown = markdown.replace(/\n{3,}/g, '\n\n');
    
    return markdown.trim();
}

// Supported file extensions
const SUPPORTED_EXTENSIONS = [
    'js', 'py', 'java', 'cpp', 'c', 'html', 'css', 'php', 'rb', 'go', 'rs', 'ts', 
    'jsx', 'tsx', 'vue', 'svelte', 'md', 'txt', 'json', 'xml', 'yaml', 'yml', 
    'toml', 'ini', 'sh', 'bat', 'ps1', 'sql', 'r', 'scala', 'kt', 'swift', 'zip'
];

// Custom alert function
function showAlert(title, message, type = 'info') {
    const modal = document.getElementById('alertModal');
    const icon = document.getElementById('alertIcon');
    const titleEl = document.getElementById('alertTitle');
    const messageEl = document.getElementById('alertMessage');
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    icon.className = `text-4xl mb-4 ${type === 'error' ? 'fas fa-exclamation-circle text-red-500' : 
                                    type === 'success' ? 'fas fa-check-circle text-green-500' : 
                                    'fas fa-info-circle text-blue-500'}`;
    
    modal.classList.remove('hidden');
}

document.getElementById('alertOkBtn').onclick = () => {
    document.getElementById('alertModal').classList.add('hidden');
};

// File upload handling
const fileDropZone = document.getElementById('fileDropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const fileItems = document.getElementById('fileItems');
const generateSection = document.getElementById('generateSection');

fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropZone.classList.add('dragover');
});

fileDropZone.addEventListener('dragleave', () => {
    fileDropZone.classList.remove('dragover');
});

fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    selectedFiles = Array.from(files).filter(file => {
        const extension = file.name.split('.').pop().toLowerCase();
        return SUPPORTED_EXTENSIONS.includes(extension);
    });

    if (selectedFiles.length === 0) {
        showAlert('No Valid Files', 'Please select code files or ZIP folders with supported extensions.', 'error');
        return;
    }

    // Check if any ZIP files are included
    const zipFiles = selectedFiles.filter(file => file.name.toLowerCase().endsWith('.zip'));
    if (zipFiles.length > 0) {
        showAlert('Folder Upload Detected', 
            `Found ${zipFiles.length} ZIP file(s). The system will automatically extract and analyze all code files within these folders.`, 
            'info');
    }

    displayFileList();
    fileList.classList.remove('hidden');
    generateSection.classList.remove('hidden');
}

function displayFileList() {
    fileItems.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded border';
        
        const isZip = file.name.toLowerCase().endsWith('.zip');
        const icon = isZip ? 'fas fa-folder-zip' : 'fas fa-file-code';
        const size = (file.size / 1024).toFixed(1);
        const sizeText = file.size > 1024 * 1024 ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` : `${size} KB`;
        
        fileItem.innerHTML = `
            <div class="flex items-center">
                <i class="${icon} text-primary mr-3"></i>
                <div>
                    <span class="font-medium">${file.name}</span>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                        ${sizeText} ${isZip ? '(Folder)' : ''}
                    </div>
                </div>
            </div>
            <button onclick="removeFile(${index})" class="text-red-500 hover:text-red-700">
                <i class="fas fa-trash"></i>
            </button>
        `;
        fileItems.appendChild(fileItem);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFileList();
    
    if (selectedFiles.length === 0) {
        fileList.classList.add('hidden');
        generateSection.classList.add('hidden');
    }
}

// GitHub repository analysis
const analyzeGithubBtn = document.getElementById('analyzeGithubBtn');
const githubUrl = document.getElementById('githubUrl');
const githubStatus = document.getElementById('githubStatus');
const githubStatusIcon = document.getElementById('githubStatusIcon');
const githubStatusText = document.getElementById('githubStatusText');

analyzeGithubBtn.addEventListener('click', async () => {
    const repoUrl = githubUrl.value.trim();
    
    if (!repoUrl) {
        showAlert('No URL Provided', 'Please enter a GitHub repository URL.', 'error');
        return;
    }
    
    if (!repoUrl.startsWith('https://github.com/')) {
        showAlert('Invalid URL', 'Please enter a valid GitHub repository URL starting with https://github.com/', 'error');
        return;
    }
    
    // Show status
    githubStatus.classList.remove('hidden');
    githubStatusIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    githubStatusText.textContent = 'Cloning repository...';
    analyzeGithubBtn.disabled = true;
    
    try {
        const response = await fetch('/analyze-github', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repo_url: repoUrl,
                style_guide: 'google'
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to analyze repository');
        }

        // Update status
        githubStatusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        githubStatusText.textContent = `Repository analyzed successfully! Processed ${result.files_processed} files.`;
        
        // Display results
        setTimeout(() => {
            githubStatus.classList.add('hidden');
            displayDocumentation(result.documentation);
            
            // Show success message
            showAlert('Repository Analyzed', 
                `Successfully analyzed ${result.files_processed} files from ${repoUrl}`, 'success');
        }, 1000);

    } catch (error) {
        githubStatusIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
        githubStatusText.textContent = `Error: ${error.message}`;
        analyzeGithubBtn.disabled = false;
        
        setTimeout(() => {
            githubStatus.classList.add('hidden');
        }, 3000);
        
        showAlert('Analysis Failed', error.message, 'error');
    }
});

// Documentation generation
document.getElementById('generateBtn').addEventListener('click', generateDocumentation);

async function generateDocumentation() {
    if (selectedFiles.length === 0) {
        showAlert('No Files Selected', 'Please select files to generate documentation.', 'error');
        return;
    }

    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const outputSection = document.getElementById('outputSection');

    progressSection.classList.remove('hidden');
    outputSection.classList.add('hidden');
    
    try {
        // Create FormData for file upload
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        progressText.textContent = 'Uploading files to server...';
        progressBar.style.width = '20%';

        // Send files to Flask backend
        const response = await fetch('/generate-documentation', {
            method: 'POST',
            body: formData
        });

        progressText.textContent = 'Analyzing files and generating documentation...';
        progressBar.style.width = '60%';

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to generate documentation');
        }

        progressText.textContent = 'Finalizing documentation...';
        progressBar.style.width = '90%';

        // Display results
        setTimeout(() => {
            progressBar.style.width = '100%';
            progressText.textContent = `Documentation generated successfully! Processed ${result.files_processed || 'multiple'} files.`;
            
            setTimeout(() => {
                progressSection.classList.add('hidden');
                displayDocumentation(result.documentation);
            }, 1000);
        }, 500);

    } catch (error) {
        progressSection.classList.add('hidden');
        showAlert('Generation Failed', error.message, 'error');
    }
}

function displayDocumentation(documentation) {
    updateGlobalDocumentation(documentation);
    
    const contentDiv = document.getElementById('documentationContent');
    
    // Since we're now getting HTML directly from the server, we can insert it directly
    contentDiv.innerHTML = documentation;
    
    // Add custom styling for better formatting
    const headings = contentDiv.querySelectorAll('h1, h2, h3, h4');
    headings.forEach(heading => {
        heading.classList.add('documentation-heading');
    });
    
    // Add syntax highlighting to code blocks if they exist
    const codeBlocks = contentDiv.querySelectorAll('pre code');
    codeBlocks.forEach(codeBlock => {
        // Add a class for styling
        codeBlock.classList.add('syntax-highlighted');
    });
    
    // Show the output section
    document.getElementById('outputSection').classList.remove('hidden');
    
    // Show the chatbot section and enable it
    if (typeof window.showChatbot === 'function') {
        window.showChatbot();
    }
    
    // Clear previous chat
    if (typeof window.clearChat === 'function') {
        window.clearChat();
    }
    
    // Scroll to output
    document.getElementById('outputSection').scrollIntoView({ behavior: 'smooth' });
}

// Copy functionality (HTML)
document.getElementById('copyBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(generatedDocumentation).then(() => {
        showAlert('Copied!', 'HTML documentation has been copied to clipboard.', 'success');
    }).catch(() => {
        showAlert('Copy Failed', 'Failed to copy documentation to clipboard.', 'error');
    });
});

// Copy functionality (Markdown)
document.getElementById('copyMarkdownBtn').addEventListener('click', () => {
    const markdownContent = htmlToMarkdown(generatedDocumentation);
    navigator.clipboard.writeText(markdownContent).then(() => {
        showAlert('Copied!', 'Markdown documentation has been copied to clipboard.', 'success');
    }).catch(() => {
        showAlert('Copy Failed', 'Failed to copy markdown to clipboard.', 'error');
    });
});

// Download functionality
document.getElementById('downloadBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/download-documentation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                documentation: generatedDocumentation
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to prepare download');
        }

        // Convert HTML to Markdown for download
        const markdownContent = htmlToMarkdown(generatedDocumentation);
        
        // Create and download the file
        const blob = new Blob([markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'project-documentation.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showAlert('Downloaded!', 'Documentation has been saved as project-documentation.md', 'success');
    } catch (error) {
        showAlert('Download Failed', error.message, 'error');
    }
});

// Fullscreen functionality
const fullscreenModal = document.getElementById('fullscreenModal');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const exitFullscreenBtn = document.getElementById('exitFullscreenBtn');
const fullscreenDocumentationContent = document.getElementById('fullscreenDocumentationContent');
const fullscreenCopyBtn = document.getElementById('fullscreenCopyBtn');
const fullscreenDownloadBtn = document.getElementById('fullscreenDownloadBtn');

// Open fullscreen view
fullscreenBtn.addEventListener('click', () => {
    if (!generatedDocumentation) {
        showAlert('No Documentation', 'Please generate documentation first.', 'error');
        return;
    }
    
    // Copy content to fullscreen modal
    fullscreenDocumentationContent.innerHTML = generatedDocumentation;
    
    // Add custom styling for better formatting
    const headings = fullscreenDocumentationContent.querySelectorAll('h1, h2, h3, h4');
    headings.forEach(heading => {
        heading.classList.add('documentation-heading');
    });
    
    // Add syntax highlighting to code blocks if they exist
    const codeBlocks = fullscreenDocumentationContent.querySelectorAll('pre code');
    codeBlocks.forEach(codeBlock => {
        codeBlock.classList.add('syntax-highlighted');
    });
    
    // Show fullscreen modal
    fullscreenModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
    
    // Focus on the modal for keyboard navigation
    fullscreenModal.focus();
});

// Close fullscreen view
function closeFullscreen() {
    fullscreenModal.classList.add('hidden');
    document.body.style.overflow = 'auto'; // Restore background scrolling
}

exitFullscreenBtn.addEventListener('click', closeFullscreen);

// Keyboard shortcuts for fullscreen
document.addEventListener('keydown', (e) => {
    // ESC key to exit fullscreen
    if (e.key === 'Escape' && !fullscreenModal.classList.contains('hidden')) {
        e.preventDefault();
        closeFullscreen();
    }
    
    // F11 key to toggle fullscreen (when documentation is available)
    if (e.key === 'F11' && generatedDocumentation) {
        e.preventDefault();
        if (fullscreenModal.classList.contains('hidden')) {
            fullscreenBtn.click();
        } else {
            closeFullscreen();
        }
    }
});

// Click outside modal to close (optional - can be removed if not desired)
fullscreenModal.addEventListener('click', (e) => {
    if (e.target === fullscreenModal) {
        closeFullscreen();
    }
});

// Fullscreen copy functionality (HTML)
fullscreenCopyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(generatedDocumentation).then(() => {
        showAlert('Copied!', 'HTML documentation has been copied to clipboard.', 'success');
    }).catch(() => {
        showAlert('Copy Failed', 'Failed to copy documentation to clipboard.', 'error');
    });
});

// Fullscreen copy functionality (Markdown)
const fullscreenCopyMarkdownBtn = document.getElementById('fullscreenCopyMarkdownBtn');
fullscreenCopyMarkdownBtn.addEventListener('click', () => {
    const markdownContent = htmlToMarkdown(generatedDocumentation);
    navigator.clipboard.writeText(markdownContent).then(() => {
        showAlert('Copied!', 'Markdown documentation has been copied to clipboard.', 'success');
    }).catch(() => {
        showAlert('Copy Failed', 'Failed to copy markdown to clipboard.', 'error');
    });
});

// Fullscreen download functionality
fullscreenDownloadBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/download-documentation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                documentation: generatedDocumentation
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to prepare download');
        }

        // Convert HTML to Markdown for download
        const markdownContent = htmlToMarkdown(generatedDocumentation);
        
        // Create and download the file
        const blob = new Blob([markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'project-documentation.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showAlert('Downloaded!', 'Documentation has been saved as project-documentation.md', 'success');
    } catch (error) {
        showAlert('Download Failed', error.message, 'error');
    }
}); 