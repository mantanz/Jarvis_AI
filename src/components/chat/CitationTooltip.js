import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const CitationTooltip = ({ 
  children, 
  citation, 
  sourceNum,
  onClick,
  className 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseEnter = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 8
    });
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  const tooltipContent = citation?.tooltip_text || citation?.content || `Source ${sourceNum}`;
  const truncatedContent = tooltipContent.length > 200 
    ? tooltipContent.slice(0, 200) + '...' 
    : tooltipContent;

  return (
    <>
      <span
        className={clsx('relative inline-block', className)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
      >
        {children}
      </span>

      <AnimatePresence>
        {isVisible && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 z-40 pointer-events-none" 
              onClick={() => setIsVisible(false)}
            />
            
            {/* Tooltip */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 10 }}
              transition={{ duration: 0.15 }}
              className="fixed z-50 pointer-events-auto"
              style={{
                left: position.x,
                top: position.y,
                transform: 'translate(-50%, -100%)'
              }}
            >
              <div className="bg-gray-900 text-white text-sm rounded-lg shadow-lg p-3 max-w-sm">
                {/* Arrow */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2">
                  <div className="border-4 border-transparent border-t-gray-900"></div>
                </div>
                
                {/* Header */}
                {citation && (
                  <div className="border-b border-gray-700 pb-2 mb-2">
                    <div className="font-medium text-blue-300">
                      Source {sourceNum}
                    </div>
                    <div className="text-xs text-gray-300">
                      {citation.filename} • Page {citation.page}
                    </div>
                    {citation.relevance_score && (
                      <div className="text-xs text-gray-400">
                        Relevance: {(citation.relevance_score * 100).toFixed(1)}%
                      </div>
                    )}
                  </div>
                )}
                
                {/* Content */}
                <div className="text-gray-100 leading-relaxed">
                  {truncatedContent}
                </div>
                
                {/* Footer */}
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <div className="text-xs text-gray-400">
                    Click to view in document
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default CitationTooltip; 