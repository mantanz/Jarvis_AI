import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X, Check, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import Button from './Button';
import LoadingSpinner from './LoadingSpinner';

const DocumentUploader = ({
  onUpload,
  onRemove,
  uploadedFiles = [],
  isUploading = false,
  uploadProgress = 0,
  className,
  maxFiles = 10,
  maxSize = 50 * 1024 * 1024, // 50MB
  ...props
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadErrors, setUploadErrors] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(({ file, errors }) => ({
        file: file.name,
        errors: errors.map(e => e.message)
      }));
      setUploadErrors(errors);
    } else {
      setUploadErrors([]);
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      onUpload?.(acceptedFiles);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles,
    maxSize,
    disabled: isUploading,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const dropzoneClasses = clsx(
    'border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer',
    {
      'border-blue-400 bg-blue-50 text-blue-600': isDragActive || dragActive,
      'border-gray-300 hover:border-gray-400 text-gray-600': !isDragActive && !dragActive && !isUploading,
      'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed': isUploading,
    },
    className
  );

  return (
    <div className="space-y-4" {...props}>
      {/* Upload Area */}
      <div {...getRootProps()} className={dropzoneClasses}>
        <input {...getInputProps()} />
        
        <motion.div
          initial={{ scale: 1 }}
          animate={{ scale: isDragActive ? 1.05 : 1 }}
          transition={{ duration: 0.2 }}
        >
          <Upload className="mx-auto h-12 w-12 mb-4" />
          
          {isUploading ? (
            <div className="space-y-2">
              <LoadingSpinner size="sm" text="Processing documents..." />
              {uploadProgress > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div 
                    className="bg-blue-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              )}
            </div>
          ) : (
            <div>
              <p className="text-lg font-medium mb-2">
                {isDragActive ? 'Drop your PDF files here' : 'Upload PDF Documents'}
              </p>
              <p className="text-sm">
                Drag and drop your PDF files here, or{' '}
                <span className="text-blue-600 font-medium">browse</span> to select files
              </p>
              <p className="text-xs mt-2 text-gray-500">
                Maximum {maxFiles} files, up to {formatFileSize(maxSize)} each
              </p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Upload Errors */}
      <AnimatePresence>
        {uploadErrors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-50 border border-red-200 rounded-lg p-4"
          >
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-red-800 mb-2">
                  Upload Errors
                </h4>
                <ul className="space-y-1">
                  {uploadErrors.map((error, index) => (
                    <li key={index} className="text-sm text-red-700">
                      <strong>{error.file}:</strong> {error.errors.join(', ')}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Uploaded Files List */}
      <AnimatePresence>
        {uploadedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <h4 className="text-sm font-medium text-gray-900 mb-3">
              Uploaded Documents ({uploadedFiles.length})
            </h4>
            
            <div className="space-y-2">
              {uploadedFiles.map((file) => (
                <motion.div
                  key={file.filename}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div className="flex items-center flex-1 min-w-0">
                    <FileText className="h-5 w-5 text-green-600 mr-3 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                    <Check className="h-4 w-4 text-green-600 ml-2" />
                  </div>
                  
                  {onRemove && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemove(file.filename)}
                      className="ml-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentUploader; 