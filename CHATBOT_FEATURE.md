# Chatbot Feature Documentation

## Overview
The Code Auto Documenter now includes an AI-powered chatbot that allows users to ask questions about their generated documentation. This feature helps users better understand their code by providing interactive assistance.

## Features

### 🤖 AI-Powered Q&A
- Ask questions about any aspect of your generated documentation
- Get detailed explanations about functions, classes, and code structure
- Receive usage examples and troubleshooting help
- Context-aware responses based on your specific project

### 💬 Interactive Chat Interface
- Modern, responsive chat UI with dark mode support
- Real-time messaging with typing indicators
- Smooth animations for better user experience
- Toggle visibility to save screen space

### 🎨 User-Friendly Design
- Clean, professional chat interface
- Color-coded messages (blue for user, purple for bot)
- Syntax highlighting for code in responses
- Responsive design that works on all devices

## How to Use

### 1. Generate Documentation
First, upload your code files or GitHub repository to generate documentation as usual.

### 2. Access the Chatbot
Once documentation is generated, the chatbot section will automatically appear below the documentation.

### 3. Ask Questions
Type your questions in the chat input field and press Enter or click Send. You can ask about:
- Specific functions or classes
- How to use certain features
- Code explanations
- Troubleshooting help
- Best practices

### 4. Example Questions
- "How do I use the main function?"
- "What does the User class do?"
- "How can I modify this code to add new features?"
- "What are the dependencies of this project?"
- "How do I handle errors in this code?"

## Technical Implementation

### Backend (Flask)
- New `/chatbot` endpoint that processes user questions
- Uses the same Gemini API for consistent AI responses
- Context-aware prompting with project documentation
- Error handling and validation

### Frontend (JavaScript)
- Separate `chatbot.js` module for clean code organization
- Real-time chat interface with message history
- Smooth animations and transitions
- Integration with existing documentation display

### Styling (CSS)
- Custom chatbot-specific styles
- Dark mode support
- Responsive design
- Smooth animations and transitions

## Files Modified/Added

### New Files
- `static/js/chatbot.js` - Chatbot functionality
- `CHATBOT_FEATURE.md` - This documentation

### Modified Files
- `enhanced_app.py` - Added chatbot endpoint
- `app.py` - Added chatbot endpoint (basic version)
- `templates/index.html` - Added chatbot UI
- `static/css/styles.css` - Added chatbot styles
- `static/js/script.js` - Integrated chatbot with documentation display

## API Endpoints

### POST /chatbot
Processes user questions about the documentation.

**Request Body:**
```json
{
    "question": "How do I use the main function?",
    "documentation": "Generated documentation HTML content"
}
```

**Response:**
```json
{
    "success": true,
    "answer": "AI-generated response in HTML format"
}
```

## Configuration

The chatbot uses the same Gemini API configuration as the main documentation generation. No additional configuration is required.

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Future Enhancements

- Chat history persistence
- Export chat conversations
- Voice input support
- Code snippet execution
- Multi-language support for questions
- Advanced code analysis features

## Troubleshooting

### Common Issues

1. **Chatbot not appearing**: Make sure documentation has been generated first
2. **Questions not sending**: Check if the input field is enabled
3. **API errors**: Verify Gemini API key is configured correctly
4. **Styling issues**: Ensure all CSS files are loaded properly

### Debug Mode

Enable Flask debug mode to see detailed error messages in the console.

## Support

For issues or questions about the chatbot feature, please check the main project documentation or create an issue in the project repository.
