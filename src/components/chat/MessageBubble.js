import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Bot, Copy, ExternalLink, Eye } from 'lucide-react';
import clsx from 'clsx';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';
import CitationTooltip from './CitationTooltip';

const MessageBubble = ({ 
  message, 
  onCopyText, 
  onOpenCitation,
  className 
}) => {
  const [showCitations, setShowCitations] = useState(false);
  const isBot = message.type === 'bot';
  const isUser = message.type === 'user';

  // Parse citations from message content
  const renderContentWithCitations = (content) => {
    if (!message.citations || message.citations.length === 0) {
      return content;
    }

    // Replace [Source X] patterns with interactive citation components
    let renderedContent = content;
    
    message.citations.forEach((citation) => {
      const citationPattern = new RegExp(`\\[Source ${citation.source_num}\\]`, 'g');
      const citationComponent = `<CitationLink data-source-num="${citation.source_num}" data-filename="${citation.filename}" data-page="${citation.page}">Source ${citation.source_num}</CitationLink>`;
      renderedContent = renderedContent.replace(citationPattern, citationComponent);
    });

    return renderedContent;
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const handleCitationClick = (sourceNum) => {
    const citation = message.citations?.find(c => c.source_num === sourceNum);
    if (citation && onOpenCitation) {
      onOpenCitation(citation);
    }
  };

  const parseContentWithCitations = (content) => {
    if (!message.citations || message.citations.length === 0) {
      return [{ type: 'text', content }];
    }

    const parts = [];
    let lastIndex = 0;
    const citationRegex = /\[Source (\d+)\]/g;
    let match;

    while ((match = citationRegex.exec(content)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index)
        });
      }

      // Add citation
      const sourceNum = parseInt(match[1]);
      const citation = message.citations.find(c => c.source_num === sourceNum);
      
      parts.push({
        type: 'citation',
        sourceNum,
        citation,
        text: match[0]
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex)
      });
    }

    return parts;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start',
        className
      )}
    >
      <div className={clsx(
        'flex items-start space-x-3 max-w-4xl',
        isUser ? 'flex-row-reverse space-x-reverse' : ''
      )}>
        {/* Avatar */}
        <div className={clsx(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-blue-600' : 'bg-gray-100'
        )}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-gray-600" />
          )}
        </div>

        {/* Message Content */}
        <div className={clsx(
          'flex flex-col',
          isUser ? 'items-end' : 'items-start'
        )}>
          {/* Message Bubble */}
          <div className={clsx(
            'rounded-lg px-4 py-3 max-w-prose',
            isUser 
              ? 'bg-blue-600 text-white' 
              : message.error
                ? 'bg-red-50 text-red-800 border border-red-200'
                : 'bg-gray-100 text-gray-900',
            message.isLoading && 'bg-gray-50'
          )}>
            {message.isLoading ? (
              <LoadingSpinner size="sm" text="Thinking..." variant={isUser ? 'white' : 'primary'} />
            ) : (
              <div className="whitespace-pre-wrap">
                {parseContentWithCitations(message.content).map((part, index) => {
                  if (part.type === 'text') {
                    return <span key={index}>{part.content}</span>;
                  } else if (part.type === 'citation') {
                    return (
                      <CitationTooltip
                        key={index}
                        citation={part.citation}
                        sourceNum={part.sourceNum}
                        onClick={() => handleCitationClick(part.sourceNum)}
                      >
                        <button
                          className={clsx(
                            'inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border mx-0.5 transition-all duration-200 cursor-pointer',
                            isUser
                              ? 'bg-blue-500 text-white border-blue-400 hover:bg-blue-400 hover:shadow-sm'
                              : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm'
                          )}
                          onClick={() => handleCitationClick(part.sourceNum)}
                          title="Hover to see source content, click to view full document"
                        >
                          Source {part.sourceNum}
                        </button>
                      </CitationTooltip>
                    );
                  }
                  return null;
                })}
              </div>
            )}
          </div>

          {/* Message Actions */}
          {!message.isLoading && (
            <div className="flex items-center space-x-2 mt-2">
              <span className="text-xs text-gray-500">
                {formatTimestamp(message.timestamp)}
              </span>
              
              {/* Copy button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onCopyText?.(message.content)}
                className="text-xs text-gray-500 hover:text-gray-700 p-1"
              >
                <Copy className="w-3 h-3" />
              </Button>

              {/* Citations toggle */}
              {message.citations && message.citations.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCitations(!showCitations)}
                  className="text-xs text-gray-500 hover:text-gray-700 p-1"
                >
                  <Eye className="w-3 h-3 mr-1" />
                  {message.citations.length} source{message.citations.length !== 1 ? 's' : ''}
                </Button>
              )}
            </div>
          )}

          {/* Citations Panel */}
          {showCitations && message.citations && message.citations.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 w-full max-w-md"
            >
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-3">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Sources</h4>
                <div className="space-y-2">
                  {message.citations.map((citation) => (
                    <div
                      key={citation.source_num}
                      className="flex items-start justify-between p-2 bg-gray-50 rounded text-xs"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900">
                          Source {citation.source_num}
                        </div>
                        <div className="text-gray-600 truncate">
                          {citation.filename} • Page {citation.page}
                        </div>
                        {citation.tooltip_text && (
                          <div className="text-gray-500 mt-1 line-clamp-3">
                            {citation.tooltip_text.slice(0, 150)}...
                          </div>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCitationClick(citation.source_num)}
                        className="ml-2 text-blue-600 hover:text-blue-700 p-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble; 