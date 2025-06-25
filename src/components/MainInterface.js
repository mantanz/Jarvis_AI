import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MessageCircle, 
  Upload, 
  Search, 
  Settings, 
  FileText, 
  Brain, 
  Plus,
  ChevronRight,
  User,
  Bot,
  Trash2,
  RefreshCw,
  Menu,
  X
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import ChatInterface from './chat/ChatInterface';
import DocumentUploader from './ui/DocumentUploader';
import Button from './ui/Button';
import LoadingSpinner from './ui/LoadingSpinner';
import clsx from 'clsx';

const MainInterface = () => {
  const { state, actions } = useApp();
  const [activeTab, setActiveTab] = useState('chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const navigate = useNavigate();

  const {
    documents,
    documentsLoading,
    isUploading,
    uploadProgress,
    messages,
    isConnected
  } = state;

  const handleUploadDocuments = async (files) => {
    try {
      await actions.uploadDocuments(files);
      setActiveTab('chat'); // Switch to chat after upload
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleClearDocuments = async () => {
    if (window.confirm('Are you sure you want to clear all documents? This action cannot be undone.')) {
      try {
        await actions.clearDocuments();
      } catch (error) {
        console.error('Clear failed:', error);
      }
    }
  };

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageCircle },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'documents', label: 'Documents', icon: FileText },
  ];

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={clsx(
        'bg-white border-r border-gray-200 transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-80'
      )}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <div>
                <h1 className="text-xl font-bold text-gray-900 flex items-center">
                  <Brain className="w-6 h-6 mr-2 text-blue-600" />
                  RAG Assistant
                </h1>
                <p className="text-sm text-gray-500">Intelligent Document Analysis</p>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2"
            >
              {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <X className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {!sidebarCollapsed && (
          <>
            {/* Connection Status */}
            <div className="p-4 border-b border-gray-200">
              <div className={clsx(
                'flex items-center text-sm',
                isConnected ? 'text-green-600' : 'text-red-600'
              )}>
                <div className={clsx(
                  'w-2 h-2 rounded-full mr-2',
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                )} />
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="p-4">
              <div className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={clsx(
                        'w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      )}
                    >
                      <Icon className="w-4 h-4 mr-3" />
                      {tab.label}
                      {tab.id === 'documents' && documents.length > 0 && (
                        <span className="ml-auto bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
                          {documents.length}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Documents Summary */}
            {documents.length > 0 && (
              <div className="p-4 border-t border-gray-200">
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-green-800">
                      Ready for Analysis
                    </h3>
                    <FileText className="w-4 h-4 text-green-600" />
                  </div>
                  <p className="text-xs text-green-700">
                    {documents.length} document{documents.length !== 1 ? 's' : ''} loaded
                  </p>
                  <div className="mt-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleClearDocuments}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Clear All
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="p-4 border-t border-gray-200 mt-auto">
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={actions.checkConnection}
                  className="w-full justify-start text-xs"
                >
                  <RefreshCw className="w-3 h-3 mr-2" />
                  Refresh Connection
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setActiveTab('upload')}
                  className="w-full justify-start text-xs"
                >
                  <Plus className="w-3 h-3 mr-2" />
                  Add Documents
                </Button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Tab Content */}
        {activeTab === 'chat' && (
          <ChatInterface className="flex-1" />
        )}

        {activeTab === 'upload' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
              <p className="text-gray-600 mb-6">
                Upload PDF documents to analyze and query with your RAG assistant.
              </p>
              
              <DocumentUploader
                onUpload={handleUploadDocuments}
                uploadedFiles={documents}
                isUploading={isUploading}
                uploadProgress={uploadProgress}
                className="mb-6"
              />

              {documents.length > 0 && (
                <div className="mt-6">
                  <Button
                    onClick={() => setActiveTab('chat')}
                    className="w-full"
                  >
                    Start Chatting with Your Documents
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Document Library</h2>
                  <p className="text-gray-600">
                    Manage your uploaded documents and view their details.
                  </p>
                </div>
                <Button
                  onClick={() => setActiveTab('upload')}
                  icon={Plus}
                >
                  Add Documents
                </Button>
              </div>

              {documentsLoading ? (
                <div className="flex justify-center py-12">
                  <LoadingSpinner size="lg" text="Loading documents..." />
                </div>
              ) : documents.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Documents Uploaded
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Upload your first PDF document to get started.
                  </p>
                  <Button
                    onClick={() => setActiveTab('upload')}
                    icon={Upload}
                  >
                    Upload Documents
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4">
                  {documents.map((doc) => (
                    <div
                      key={doc.filename}
                      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <FileText className="w-8 h-8 text-blue-600 mt-1" />
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-medium text-gray-900 truncate">
                              {doc.filename}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {formatFileSize(doc.size)}
                            </p>
                            <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                              <span>PDF Document</span>
                              <span>•</span>
                              <span>Ready for analysis</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigate(`/pdf-viewer?file=${doc.filename}`)}
                          >
                            View
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MainInterface; 