import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot, Copy, ExternalLink, FileText } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';
import CitationTooltip from './CitationTooltip';
import MessageBubble from './MessageBubble';
import clsx from 'clsx';
import toast from 'react-hot-toast';

const ChatInterface = ({ className }) => {
  const { state, actions } = useApp();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const {
    messages,
    isQuerying,
    documents,
    selectedDocuments,
    isConnected,
    connectionError
  } = state;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isQuerying) return;

    const query = inputValue.trim();
    setInputValue('');

    try {
      await actions.queryDocuments(query);
    } catch (error) {
      console.error('Query failed:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard');
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  const openCitationInViewer = (citation) => {
    // Find the message that contains this citation to get all citation data
    const messageWithCitation = messages.find(msg => 
      msg.citations && msg.citations.some(c => c.source_num === citation.source_num)
    );
    
    if (messageWithCitation && messageWithCitation.citations) {
      // Filter citations to only include those from the same document
      const documentCitations = messageWithCitation.citations.filter(c => 
        c.filename === citation.filename
      );
      
      // Renumber the filtered citations sequentially
      const renumberedCitations = documentCitations.map((c, index) => ({
        ...c,
        display_source_num: index + 1,
        original_source_num: c.source_num
      }));
      
      // Find the active citation in the renumbered list
      const activeCitation = renumberedCitations.find(c => 
        c.original_source_num === citation.source_num
      );
      const activeChunk = activeCitation ? `chunk-${activeCitation.display_source_num}` : `chunk-1`;
      
      // Debug logging (can be removed in production)
      console.log('Opening PDF viewer with:', {
        citation,
        filteredCitations: renumberedCitations,
        activeChunk,
        filename: citation.filename,
        totalCitationsForDocument: renumberedCitations.length
      });
      
      actions.setActiveCitation(citation);
      
      // Clean up old PDF viewer data from localStorage (older than 1 hour)
      const oneHourAgo = Date.now() - (60 * 60 * 1000);
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith('pdfViewer_')) {
          const timestamp = parseInt(key.split('_')[1]);
          if (timestamp && timestamp < oneHourAgo) {
            localStorage.removeItem(key);
          }
        }
      });

      // Store citation data in both localStorage and window object for reliability
      const sessionKey = `pdfViewer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const sessionData = {
        citations: renumberedCitations,
        activeChunk: activeChunk,
        filename: citation.filename
      };
      
      // Store in localStorage (more reliable across tabs than sessionStorage)
      localStorage.setItem(sessionKey, JSON.stringify(sessionData));
      
      // Also store in window object as backup
      if (!window.pdfViewerData) {
        window.pdfViewerData = {};
      }
      window.pdfViewerData[sessionKey] = sessionData;
      
      // Create URL with small citation data if possible, otherwise use session key
      const citationsData = encodeURIComponent(JSON.stringify(renumberedCitations));
      let pdfViewerURL;
      
      if (citationsData.length < 1500) {
        // Small enough for URL - use direct approach
        pdfViewerURL = `/pdf-viewer?file=${encodeURIComponent(citation.filename)}&chunks=${citationsData}&active=${activeChunk}`;
        console.log('Using URL-based approach (small data)');
      } else {
        // Too large - use session approach
        pdfViewerURL = `/pdf-viewer?file=${encodeURIComponent(citation.filename)}&session=${sessionKey}&active=${activeChunk}`;
        console.log('Using session-based approach (large data)');
      }
      
      console.log('Generated PDF viewer URL:', pdfViewerURL);
      console.log('Citation data:', sessionData);
      console.log('URL length:', pdfViewerURL.length);
      
      window.open(pdfViewerURL, '_blank');
    } else {
      // Fallback to simple navigation
      window.open(`/pdf-viewer?file=${encodeURIComponent(citation.filename)}&source=${citation.source_num}`, '_blank');
    }
  };

  // Sample suggestions when no documents are uploaded
  const sampleQueries = [
    'How does machine learning work?',
    'What are the benefits of AI?',
    'Explain neural networks',
    'What is deep learning?'
  ];

  if (!isConnected && connectionError) {
    return (
      <div className={clsx('flex items-center justify-center h-full', className)}>
        <div className="text-center p-8">
          <div className="text-red-500 mb-4">
            <Bot className="w-16 h-16 mx-auto mb-4 opacity-50" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Connection Error</h3>
          <p className="text-gray-600">Unable to connect to the backend service.</p>
          <Button 
            className="mt-4" 
            onClick={actions.checkConnection}
            variant="outline"
          >
            Retry Connection
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('flex flex-col h-full bg-white', className)}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onCopyText={copyToClipboard}
              onOpenCitation={openCitationInViewer}
            />
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {isQuerying && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-3 max-w-3xl">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-blue-600" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <LoadingSpinner size="sm" text="Thinking..." />
              </div>
            </div>
          </motion.div>
        )}

        {/* Sample queries when no documents */}
        {messages.length <= 1 && documents.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-8"
          >
            <div className="mb-6">
              <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Documents Uploaded
              </h3>
              <p className="text-gray-600">
                Upload some PDF documents to get started with intelligent search and analysis.
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-sm text-gray-500 mb-3">Or try these sample queries:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {sampleQueries.map((query, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => setInputValue(query)}
                    className="text-xs"
                  >
                    {query}
                  </Button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-gray-50 p-4">
        {/* Selected Documents Indicator */}
        {documents.length > 0 && (
          <div className="mb-3 p-2 bg-white rounded-lg border border-gray-200">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <FileText className="w-3 h-3 text-gray-500" />
                <span className="text-gray-600">
                  {selectedDocuments.length > 0 ? (
                    <>
                      <span className="font-medium text-green-600">{selectedDocuments.length}</span> of {documents.length} documents selected for queries
                    </>
                  ) : (
                    <span className="text-red-600">No documents selected - select documents to enable queries</span>
                  )}
                </span>
              </div>
              {selectedDocuments.length > 0 && (
                <button
                  type="button"
                  onClick={() => actions.setActiveTab?.('documents')}
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  Manage
                </button>
              )}
            </div>
            {selectedDocuments.length > 0 && selectedDocuments.length <= 3 && (
              <div className="mt-1 text-xs text-gray-500">
                Using: {selectedDocuments.join(', ')}
              </div>
            )}
            {selectedDocuments.length > 3 && (
              <div className="mt-1 text-xs text-gray-500">
                Using: {selectedDocuments.slice(0, 2).join(', ')} and {selectedDocuments.length - 2} more...
              </div>
            )}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                selectedDocuments.length > 0 
                  ? `Ask anything about your ${selectedDocuments.length} selected document${selectedDocuments.length !== 1 ? 's' : ''}...` 
                  : documents.length > 0
                    ? "Select documents first, then ask questions..."
                    : "Upload documents first, then ask questions..."
              }
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="1"
              style={{
                minHeight: '48px',
                maxHeight: '120px',
                resize: 'none'
              }}
              disabled={isQuerying}
            />
            
            {/* Character count or document count */}
            <div className="absolute bottom-2 right-2 text-xs text-gray-400">
              {selectedDocuments.length > 0 && (
                <span>{selectedDocuments.length}/{documents.length} selected</span>
              )}
            </div>
          </div>

          <Button
            type="submit"
            disabled={!inputValue.trim() || isQuerying || selectedDocuments.length === 0}
            loading={isQuerying}
            icon={Send}
            className="px-6"
          >
            Send
          </Button>
        </form>

        {/* Keyboard shortcut hint */}
        <p className="text-xs text-gray-500 mt-2 text-center">
          Press Cmd/Ctrl + Enter to send
        </p>
      </div>
    </div>
  );
};

export default ChatInterface; 