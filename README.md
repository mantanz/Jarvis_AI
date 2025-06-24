# React PDF Viewer with RAG Capabilities

A modern React-based PDF viewer that replaces the Streamlit functionality with a sleek, chat-like interface. This application provides PDF viewing capabilities with advanced text highlighting and citation source navigation.

## Features

### Main Interface
- **Modern Chat UI**: Clean, intuitive interface similar to popular chat applications
- **File Upload**: Drag-and-drop or browse to upload PDF files
- **Real-time Chat**: Interactive chat with AI assistant for document analysis
- **Sample Searches**: Quick access to common questions
- **Google Integration**: Display relevant search results
- **Notepad**: Built-in note-taking functionality

### PDF Viewer
- **Advanced PDF Rendering**: Uses PDF.js for high-quality document display
- **Text Highlighting**: Intelligent highlighting based on first/last 5 words algorithm
- **Citation Navigation**: Click citation sources to jump to relevant text
- **Zoom Controls**: In/out zoom functionality
- **Page Navigation**: Easy navigation between document pages
- **Responsive Design**: Works on different screen sizes

### Text Highlighting Algorithm
The application uses an advanced highlighting system that:
1. Extracts the first 5 and last 5 words from citation chunks
2. Builds a continuous text map from PDF text layers
3. Identifies text boundaries using partial matching fallbacks
4. Highlights entire text regions rather than scattered words
5. Provides smooth scrolling to highlighted content

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd react-pdf-viewer
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

### Main Interface
1. **Upload Documents**: Use the drag-and-drop area or browse button to upload PDF files
2. **Start Chatting**: Ask questions about your uploaded documents
3. **Use Samples**: Click on sample searches for quick queries
4. **Take Notes**: Use the notepad for important observations

### PDF Viewer
1. **Access Viewer**: Click on uploaded PDF files to open the viewer
2. **Navigate Citations**: Use the left sidebar to click on citation sources
3. **View Highlights**: Text will be automatically highlighted when citations are selected
4. **Control View**: Use zoom and page navigation controls in the header
5. **Return to Chat**: Click "Back to Chat" to return to the main interface

## Project Structure

```
src/
├── components/
│   ├── MainInterface.js    # Main chat interface
│   └── PDFViewer.js        # PDF viewer with highlighting
├── index.css              # Global styles and Tailwind imports
├── App.js                 # Main app component with routing
└── index.js               # React entry point

public/
└── index.html             # HTML template

Configuration files:
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
└── postcss.config.js      # PostCSS configuration
```

## Key Technologies

- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing for navigation
- **Tailwind CSS**: Utility-first CSS framework for styling
- **PDF.js**: Mozilla's PDF rendering library
- **Lucide React**: Beautiful, customizable icons
- **PostCSS**: CSS processing for Tailwind

## Features Comparison

| Feature | Streamlit Version | React Version |
|---------|------------------|---------------|
| PDF Rendering | HTML embedding | PDF.js canvas |
| UI Framework | Streamlit components | React + Tailwind |
| Styling | Custom CSS + Streamlit | Tailwind CSS |
| Navigation | URL parameters | React Router |
| Interactivity | Server-side | Client-side |
| Performance | Server dependent | Client optimized |
| Customization | Limited | Highly customizable |

## Advanced Highlighting System

The React version implements an improved text highlighting algorithm:

```javascript
// Extract boundary words
const firstWords = words.slice(0, 5).join(' ').toLowerCase();
const lastWords = words.slice(-5).join(' ').toLowerCase();

// Build continuous text mapping
const continuousText = spans.map(span => span.textContent).join(' ');

// Find text boundaries with fallback matching
let startPos = continuousText.indexOf(firstWords);
let endPos = continuousText.lastIndexOf(lastWords);

// Highlight all spans within boundaries
spanTextMap.forEach(spanInfo => {
  if (spanInfo.endIndex > startPos && spanInfo.startIndex < endPos) {
    highlightSpan(spanInfo.span);
  }
});
```

## Customization

### Styling
- Modify `tailwind.config.js` to change color schemes
- Update `src/index.css` for custom animations and effects
- Adjust component styles in individual React components

### Functionality
- Add new chat features in `MainInterface.js`
- Enhance PDF rendering in `PDFViewer.js`
- Implement additional highlighting algorithms

## Development

### Available Scripts
- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App (not recommended)

### Adding Features
1. Create new components in `src/components/`
2. Add routes in `App.js` if needed
3. Update styling with Tailwind classes
4. Test functionality across different browsers

## Production Deployment

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Deploy the `build` folder** to your preferred hosting service:
   - Netlify
   - Vercel
   - AWS S3 + CloudFront
   - GitHub Pages

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please create an issue in the repository or contact the development team. 