# Document Navigation Features

This document explains the new document navigation functionality added to the RAG Pipeline application. These features allow users to easily navigate from citations back to the original source documents.

## 🚀 Features Overview

### 1. **Citation-to-Document Navigation**
- Click on citation links to open original documents
- Navigate directly to specific pages and paragraphs
- Multiple viewing options: system viewer, embedded viewer, download

### 2. **Document Browser**
- Browse all available documents in the data directory
- Quick access to open, view, or download any document
- Document size and metadata information

### 3. **Embedded PDF Viewer**
- View PDFs directly within the application
- Full-featured PDF viewer with zoom, navigation controls
- No need to leave the application to read source documents

### 4. **Enhanced Tooltips**
- Existing hover tooltips now include document location information
- Quick preview of where the information comes from
- Right-click hints for opening documents

## 📖 How to Use

### Basic Navigation

1. **From Chat Responses:**
   - After receiving a response with citations, expand the "📚 Sources" section
   - Each source now has navigation buttons:
     - 🔗 **Open**: Opens document in your system's PDF viewer
     - 📖 **View**: Opens document in embedded viewer within the app
     - 💾 **Download**: Downloads the PDF file

2. **From Document Browser:**
   - Click "📖 Browse Documents" in the sidebar
   - Browse all available documents
   - Use the same navigation options for any document

### Advanced Features

1. **Precise Navigation:**
   - Citations now include paragraph and chunk information
   - Navigation attempts to go to the exact location where information was extracted
   - Page-level navigation as fallback

2. **Multiple Viewing Options:**
   - **System Viewer**: Uses your computer's default PDF application
   - **Embedded Viewer**: Full-featured PDF viewer within the app
   - **Download**: Save document locally for offline viewing

3. **Enhanced Source Information:**
   - Hover over citation links to see enhanced tooltips
   - Location information includes page, paragraph, and chunk details
   - Visual indicators for document availability

## 🔧 Technical Details

### Navigation URL Formats

The system generates different types of navigation URLs:

1. **System URLs**: `file:///absolute/path/to/document.pdf#page=5`
2. **Web URLs**: `/document-viewer?file=document.pdf&page=5&paragraph=2`
3. **Embedded URLs**: `#view-document-page-5-para-2`

### Document Location Tracking

Each citation includes:
- **Filename**: Original PDF filename
- **Page**: Page number where information appears
- **Paragraph**: Paragraph number within the page
- **Chunk**: Specific chunk within the paragraph

### Browser Compatibility

- **Chrome/Edge**: Full support for all features
- **Firefox**: Full support with security settings adjusted
- **Safari**: Limited file:// URL support, use embedded viewer
- **Mobile**: Embedded viewer recommended

## 🛠️ Installation & Setup

No additional setup required! The navigation features are automatically available if the required modules are present.

### Optional Dependencies

For enhanced PDF viewing capabilities:
```bash
pip install streamlit-components-base64
```

## 🎯 Usage Examples

### Example 1: Quick Document Access
```
1. Ask: "What is machine learning?"
2. Get response with citations [Source 1], [Source 2]
3. Expand "📚 Sources" section
4. Click 🔗 "Open" to view original document
5. Document opens at the relevant page
```

### Example 2: Detailed Review
```
1. After getting a response, click 📖 "View Page X"
2. Embedded PDF viewer opens showing the exact page
3. Use zoom controls to read details
4. Navigate between pages using built-in controls
5. Return to chat to continue conversation
```

### Example 3: Document Exploration
```
1. Click "📖 Browse Documents" in sidebar
2. See all available documents with sizes
3. Click on any document to open/view/download
4. Explore documents independently of chat context
```

## 🔒 Security & Privacy

- **Local Files Only**: All documents are stored locally in the `data/` directory
- **No External Requests**: PDF viewing works entirely offline
- **Browser Security**: File:// URLs subject to browser security policies
- **Data Privacy**: No document content sent to external servers

## 🐛 Troubleshooting

### Document Won't Open
- **Issue**: Clicking navigation buttons doesn't open document
- **Solution**: Try the embedded viewer or download option
- **Cause**: Browser security settings may block file:// URLs

### PDF Viewer Not Loading
- **Issue**: Embedded PDF viewer shows blank or error
- **Solution**: Check browser console for errors, try different browser
- **Cause**: Large PDF files or browser compatibility issues

### Navigation Buttons Missing
- **Issue**: Only basic citation info shown, no navigation buttons
- **Solution**: Check that citation_navigation.py module is present
- **Cause**: Import error or missing dependencies

### Incorrect Page Navigation
- **Issue**: Document opens but not at the right page
- **Solution**: PDF viewer may not support page anchors, navigate manually
- **Cause**: PDF viewer limitations or corrupted page metadata

## 📈 Performance Notes

- **Large PDFs**: May take time to load in embedded viewer
- **Multiple Documents**: Opening many documents simultaneously may impact performance
- **Browser Memory**: Embedded viewer keeps PDFs in memory while open

## 🔄 Backward Compatibility

All existing functionality remains unchanged:
- Original tooltip system still works
- Basic citation display unchanged
- No breaking changes to existing workflows

## 🚀 Future Enhancements

Planned improvements:
- **Text Search**: Find specific terms within opened documents
- **Annotation Support**: Add notes and highlights
- **Document Comparison**: View multiple sources side-by-side
- **Mobile Optimization**: Better mobile PDF viewing experience

## 💡 Tips & Best Practices

1. **Use Embedded Viewer** for detailed reading within the app
2. **Use System Viewer** for full-featured PDF experience
3. **Download Documents** for offline access or sharing
4. **Check Browser Settings** if file:// URLs don't work
5. **Use Document Browser** to explore all available sources
6. **Hover Over Citations** for quick source previews

## 📞 Support

If you experience issues with document navigation:
1. Check browser console for error messages
2. Try different navigation options (embedded vs system)
3. Verify PDF files are accessible in the data directory
4. Test with different browsers if needed

The navigation features are designed to enhance your RAG experience by providing seamless access to source documents while maintaining all existing functionality. 