import React from 'react';
import { FileText, Check, Square, CheckSquare } from 'lucide-react';
import Button from './Button';
import clsx from 'clsx';

const DocumentSelector = ({ 
  documents = [], 
  selectedDocuments = [], 
  onToggleDocument, 
  onSelectAll, 
  onDeselectAll,
  className = '' 
}) => {
  const allSelected = documents.length > 0 && selectedDocuments.length === documents.length;
  const someSelected = selectedDocuments.length > 0 && selectedDocuments.length < documents.length;

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (documents.length === 0) {
    return (
      <div className={clsx('text-center py-8', className)}>
        <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
        <p className="text-gray-500 text-sm">No documents available</p>
      </div>
    );
  }

  return (
    <div className={clsx('bg-white border border-gray-200 rounded-lg', className)}>
      {/* Header with select all controls */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={allSelected ? onDeselectAll : onSelectAll}
              className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              {allSelected ? (
                <CheckSquare className="w-4 h-4 text-blue-600" />
              ) : someSelected ? (
                <div className="w-4 h-4 bg-blue-600 rounded border flex items-center justify-center">
                  <div className="w-2 h-0.5 bg-white rounded"></div>
                </div>
              ) : (
                <Square className="w-4 h-4 text-gray-400" />
              )}
              <span>
                {allSelected ? 'Deselect All' : 'Select All'}
              </span>
            </button>
          </div>
          <div className="text-xs text-gray-500">
            {selectedDocuments.length} of {documents.length} selected
          </div>
        </div>
      </div>

      {/* Scrollable document list */}
      <div className="max-h-96 overflow-y-auto">
        {documents.map((doc, index) => {
          const isSelected = selectedDocuments.includes(doc.filename);
          
          return (
            <div
              key={doc.filename}
              className={clsx(
                'flex items-center space-x-3 p-4 hover:bg-gray-50 cursor-pointer transition-colors',
                index !== documents.length - 1 && 'border-b border-gray-100',
                isSelected && 'bg-blue-50'
              )}
              onClick={() => onToggleDocument(doc.filename)}
            >
              {/* Checkbox */}
              <div className="flex-shrink-0">
                {isSelected ? (
                  <CheckSquare className="w-5 h-5 text-blue-600" />
                ) : (
                  <Square className="w-5 h-5 text-gray-400 hover:text-gray-600" />
                )}
              </div>

              {/* Document icon */}
              <div className="flex-shrink-0">
                <FileText className={clsx(
                  'w-6 h-6',
                  isSelected ? 'text-blue-600' : 'text-gray-400'
                )} />
              </div>

              {/* Document info */}
              <div className="flex-1 min-w-0">
                <h4 className={clsx(
                  'text-sm font-medium truncate',
                  isSelected ? 'text-blue-900' : 'text-gray-900'
                )}>
                  {doc.filename}
                </h4>
                <div className="flex items-center space-x-3 text-xs text-gray-500 mt-1">
                  <span>{formatFileSize(doc.size)}</span>
                  <span>•</span>
                  <span>PDF Document</span>
                  {isSelected && (
                    <>
                      <span>•</span>
                      <span className="text-blue-600 font-medium">Selected for analysis</span>
                    </>
                  )}
                </div>
              </div>

              {/* Selection indicator */}
              {isSelected && (
                <div className="flex-shrink-0">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer with selection summary */}
      {selectedDocuments.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <span className="font-medium text-blue-600">{selectedDocuments.length}</span> document{selectedDocuments.length !== 1 ? 's' : ''} selected for RAG queries
            </div>
            <div className="flex space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={onDeselectAll}
                className="text-xs"
              >
                Clear Selection
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentSelector; 