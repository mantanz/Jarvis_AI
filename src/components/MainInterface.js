import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MessageCircle, 
  Upload, 
  Search, 
  Send, 
  FileText, 
  Brain, 
  Plus,
  ChevronRight,
  User,
  Bot
} from 'lucide-react';

const MainInterface = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: "Hi there! I'm here to help you understand your sources. What would you like to know?",
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedSources, setSelectedSources] = useState(new Set());
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const chats = [
    { id: 1, name: 'New Chat', icon: Plus, active: true },
    { id: 2, name: 'Research Summary', icon: Brain, active: false },
    { id: 3, name: 'Analyze This Topic', icon: Search, active: false },
  ];

  const sampleSearches = [
    'How does GPT-4 work?',
    'What is machine learning?',
    'Explain neural networks',
    'Types of AI models'
  ];

  const googleResult = {
    title: 'Google Search: How does GPT-4 work?',
    description: 'GPT-4 is a large multimodal model (accepting image and text inputs, emitting text outputs) that, while less capable than humans in many real-world scenarios, exhibits human-level performance on various professional and academic benchmarks.',
    source: 'OpenAI'
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, newMessage]);
    const currentQuery = inputMessage;
    setInputMessage('');

    // Show loading state
    const loadingMessage = {
      type: 'bot',
      content: 'Analyzing your documents...',
      timestamp: new Date().toLocaleTimeString(),
      isLoading: true
    };
    setMessages(prev => [...prev, loadingMessage]);

    try {
      // Simple RAG: Search through uploaded files
      const response = await performRAGSearch(currentQuery);
      
      // Remove loading message and add real response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        return [...withoutLoading, {
          type: 'bot',
          content: response,
          timestamp: new Date().toLocaleTimeString()
        }];
      });
    } catch (error) {
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        return [...withoutLoading, {
          type: 'bot',
          content: 'Sorry, I encountered an error while analyzing your documents. Please try again.',
          timestamp: new Date().toLocaleTimeString()
        }];
      });
    }
  };

  const performRAGSearch = async (query) => {
    const selectedFiles = uploadedFiles.filter(file => selectedSources.has(file.id));
    
    if (selectedFiles.length === 0) {
      return "I don't see any selected sources to analyze. Please upload some PDF files and select them as sources, then I'll help you find relevant information.";
    }

    try {
      // Simple keyword-based search through selected files only
      const queryWords = query.toLowerCase().split(/\s+/);
      let relevantContent = [];

      for (const file of selectedFiles) {
        if (file.type === 'application/pdf') {
          const textContent = await extractTextFromPDF(file.file);
          const sentences = textContent.split(/[.!?]+/).filter(s => s.trim().length > 20);
          
          // Find sentences that contain query words
          const matches = sentences.filter(sentence => {
            const sentenceLower = sentence.toLowerCase();
            return queryWords.some(word => sentenceLower.includes(word));
          });

          relevantContent.push(...matches.slice(0, 3)); // Top 3 matches per file
        }
      }

      if (relevantContent.length === 0) {
        return `I couldn't find specific information about "${query}" in your uploaded documents. The documents might not contain this information, or you could try rephrasing your question.`;
      }

      const response = `Based on your uploaded documents, here's what I found about "${query}":\n\n` +
        relevantContent.slice(0, 3).map((content, index) => 
          `${index + 1}. ${content.trim()}`
        ).join('\n\n') +
        `\n\nWould you like me to show you the specific locations in the documents where this information appears?`;

      return response;
    } catch (error) {
      console.error('Error in RAG search:', error);
      return "I encountered an error while searching through your documents. Please try again.";
    }
  };

  const extractTextFromPDF = async (file) => {
    try {
      const pdfjs = await import('pdfjs-dist');
      pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
      
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjs.getDocument(arrayBuffer).promise;
      let fullText = '';

      // Extract text from all pages
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');
        fullText += pageText + ' ';
      }

      return fullText;
    } catch (error) {
      console.error('Error extracting text from PDF:', error);
      return '';
    }
  };

  const handleFileUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    // Auto-select newly uploaded files
    const newFileIds = newFiles.map(file => file.id);
    setSelectedSources(prev => new Set([...prev, ...newFileIds]));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const toggleSourceSelection = (fileId) => {
    setSelectedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const openPDFViewer = async (file) => {
    try {
      // Process the actual PDF file
      const arrayBuffer = await file.file.arrayBuffer();
      const fileData = Array.from(new Uint8Array(arrayBuffer));
      
      // Extract text from PDF for chunking (simplified version)
      const chunks = await extractPDFChunks(file.file);

      const params = new URLSearchParams({
        file: file.name,
        chunks: JSON.stringify(chunks),
        active: chunks.length > 0 ? `chunk-${chunks[0].source_num}` : '',
        fileData: JSON.stringify(fileData)
      });

      navigate(`/pdf-viewer?${params.toString()}`);
    } catch (error) {
      console.error('Error opening PDF viewer:', error);
      alert('Error opening PDF file. Please try again.');
    }
  };

  const extractPDFChunks = async (file) => {
    try {
      const pdfjs = await import('pdfjs-dist');
      pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
      
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjs.getDocument(arrayBuffer).promise;
      const chunks = [];

      // Extract text from each page
      for (let pageNum = 1; pageNum <= Math.min(pdf.numPages, 5); pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const text = textContent.items.map(item => item.str).join(' ');
        
        if (text.trim()) {
          // Create chunks from page text
          const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 20);
          sentences.forEach((sentence, index) => {
            if (sentence.trim()) {
              chunks.push({
                source_num: chunks.length + 1,
                page: pageNum,
                tooltip_text: sentence.trim(),
                content: sentence.trim().substring(0, 100) + '...'
              });
            }
          });
        }
      }

      return chunks.slice(0, 10); // Limit to first 10 chunks
    } catch (error) {
      console.error('Error extracting PDF chunks:', error);
      return [];
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Chats</h2>
          <div className="space-y-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${
                  chat.active 
                    ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                    : 'hover:bg-gray-50 text-gray-700'
                }`}
              >
                <chat.icon className="w-5 h-5 mr-3" />
                <span className="font-medium">{chat.name}</span>
                <ChevronRight className="w-4 h-4 ml-auto" />
              </div>
            ))}
          </div>
        </div>

        {/* File Upload Area */}
        <div className="p-4 flex-1">
          <div
            className={`drag-drop-zone rounded-lg p-8 text-center ${
              dragOver ? 'drag-over' : ''
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium text-gray-800 mb-2">
              Drag and drop files here
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Or, browse your computer
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Browse
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              className="hidden"
              onChange={(e) => handleFileUpload(e.target.files)}
            />
          </div>

          {/* Select Source */}
          {uploadedFiles.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Select Source
              </h3>
              <div className="space-y-2">
                {uploadedFiles.map((file) => {
                  const isSelected = selectedSources.has(file.id);
                  return (
                    <div
                      key={file.id}
                      className={`flex items-center p-3 rounded-lg border transition-all duration-200 ${
                        isSelected 
                          ? 'bg-blue-50 border-blue-300 shadow-sm' 
                          : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                      }`}
                    >
                      {/* Selection Checkbox */}
                      <button
                        onClick={() => toggleSourceSelection(file.id)}
                        className={`w-5 h-5 rounded border-2 flex items-center justify-center mr-3 transition-colors ${
                          isSelected
                            ? 'bg-blue-500 border-blue-500 text-white'
                            : 'border-gray-300 hover:border-blue-400'
                        }`}
                      >
                        {isSelected && (
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </button>

                      {/* File Icon */}
                      <FileText className={`w-4 h-4 mr-2 ${isSelected ? 'text-blue-600' : 'text-blue-500'}`} />
                      
                      {/* File Info */}
                      <div 
                        className="flex-1 min-w-0 cursor-pointer"
                        onClick={() => file.type === 'application/pdf' && openPDFViewer(file)}
                      >
                        <p className={`text-sm font-medium truncate ${
                          isSelected ? 'text-blue-900' : 'text-gray-800'
                        }`}>
                          {file.name}
                        </p>
                        <p className={`text-xs ${
                          isSelected ? 'text-blue-600' : 'text-gray-500'
                        }`}>
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>

                      {/* Selected Badge */}
                      {isSelected && (
                        <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded-full font-medium">
                          Selected
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Selection Summary */}
              <div className="mt-2 text-xs text-gray-600">
                {selectedSources.size} of {uploadedFiles.length} source{uploadedFiles.length !== 1 ? 's' : ''} selected
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`chat-message flex ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`flex items-start max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white ml-4'
                      : 'bg-white text-gray-800 border border-gray-200 mr-4'
                  }`}
                >
                  {message.type === 'bot' && (
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                      <Bot className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                  <div className="flex-1">
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp}
                    </p>
                  </div>
                  {message.type === 'user' && (
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center ml-3 flex-shrink-0">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center space-x-4">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask a question about your sources"
                  className="w-full px-4 py-3 pr-12 bg-gray-100 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
                />
                <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
              <button
                onClick={handleSendMessage}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Sample Search */}
      <div className="w-80 bg-white border-l border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Sample Search</h2>
        
        {/* Sample Questions */}
        <div className="mb-6">
          {sampleSearches.map((search, index) => (
            <div
              key={index}
              className="flex items-center p-3 hover:bg-gray-50 rounded-lg cursor-pointer mb-2"
              onClick={() => setInputMessage(search)}
            >
              <Search className="w-4 h-4 mr-3 text-gray-400" />
              <span className="text-sm text-gray-700">{search}</span>
            </div>
          ))}
        </div>

        {/* Google Result */}
        <div className="border-t pt-4">
          <h3 className="font-semibold text-gray-800 mb-2">Top Google Result:</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">
              {googleResult.title}
            </h4>
            <p className="text-sm text-gray-700 mb-2">
              {googleResult.description}
            </p>
            <p className="text-xs text-gray-500">
              [source: {googleResult.source}]
            </p>
          </div>
        </div>

        {/* Notepad */}
        <div className="mt-6">
          <h3 className="font-semibold text-gray-800 mb-2">Notepad</h3>
          <textarea
            placeholder="Take notes here..."
            className="w-full h-32 p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
      </div>
    </div>
  );
};

export default MainInterface; 