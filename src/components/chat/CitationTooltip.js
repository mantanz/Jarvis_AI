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
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Calculate optimal position
    let x = rect.left + rect.width / 2;
    let y = rect.top - 8;
    
    // Adjust horizontal position if tooltip would go off-screen
    if (x + 400 > viewportWidth) { // 400px is approximate tooltip width
      x = viewportWidth - 420; // Leave some margin
    } else if (x - 400 < 0) {
      x = 20; // Minimum left margin
    }
    
    // Adjust vertical position if tooltip would go off-screen
    if (y - 200 < 0) { // If not enough space above
      y = rect.bottom + 8; // Show below instead
    }
    
    setPosition({ x, y });
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  const tooltipContent = citation?.tooltip_text || citation?.content || `Source ${sourceNum}`;
  // Show the full chunk content without truncation
  const fullContent = tooltipContent;

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
              <div className="bg-gray-900 text-white text-sm rounded-lg shadow-xl border border-gray-700 p-4 max-w-2xl max-h-96 overflow-y-auto backdrop-blur-sm scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
                {/* Arrow */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2">
                  <div className="border-4 border-transparent border-t-gray-900"></div>
                </div>
                
                {/* Header */}
                {citation && (
                  <div className="border-b border-gray-700 pb-2 mb-3">
                    <div className="font-medium text-blue-300">
                      Source {sourceNum}
                    </div>
                    <div className="text-xs text-gray-300">
                      {citation.filename} • Page {citation.page}
                    </div>
                  </div>
                )}
                
                {/* Content */}
                <div className="text-gray-100 leading-relaxed whitespace-pre-wrap text-sm">
                  {fullContent}
                </div>
                
                {/* Footer */}
                <div className="mt-3 pt-2 border-t border-gray-700">
                  <div className="text-xs text-gray-400">
                    Click to view full document
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