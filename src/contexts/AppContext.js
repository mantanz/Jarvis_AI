import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  // Documents
  documents: [],
  documentsLoading: false,
  documentsError: null,
  
  // Chat/Messages
  messages: [
    {
      id: 1,
      type: 'bot',
      content: "Hi there! I'm your RAG assistant. Upload some PDF documents and I'll help you find information from them. What would you like to know?",
      timestamp: new Date().toISOString(),
    }
  ],
  
  // Query state
  currentQuery: '',
  isQuerying: false,
  queryError: null,
  
  // UI state
  uploadProgress: 0,
  isUploading: false,
  uploadError: null,
  
  // PDF Viewer state
  currentPDFData: null,
  pdfViewerMode: 'embedded', // 'embedded' | 'standalone'
  
  // Citations
  activeCitation: null,
  citationHighlights: [],
  
  // Application state
  isConnected: false,
  connectionError: null,
};

// Action types
const ActionTypes = {
  // Documents
  SET_DOCUMENTS: 'SET_DOCUMENTS',
  SET_DOCUMENTS_LOADING: 'SET_DOCUMENTS_LOADING',
  SET_DOCUMENTS_ERROR: 'SET_DOCUMENTS_ERROR',
  ADD_DOCUMENT: 'ADD_DOCUMENT',
  REMOVE_DOCUMENT: 'REMOVE_DOCUMENT',
  
  // Messages
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_MESSAGE: 'UPDATE_MESSAGE',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  
  // Query
  SET_CURRENT_QUERY: 'SET_CURRENT_QUERY',
  SET_IS_QUERYING: 'SET_IS_QUERYING',
  SET_QUERY_ERROR: 'SET_QUERY_ERROR',
  
  // Upload
  SET_UPLOAD_PROGRESS: 'SET_UPLOAD_PROGRESS',
  SET_IS_UPLOADING: 'SET_IS_UPLOADING',
  SET_UPLOAD_ERROR: 'SET_UPLOAD_ERROR',
  
  // PDF Viewer
  SET_PDF_DATA: 'SET_PDF_DATA',
  SET_PDF_VIEWER_MODE: 'SET_PDF_VIEWER_MODE',
  
  // Citations
  SET_ACTIVE_CITATION: 'SET_ACTIVE_CITATION',
  SET_CITATION_HIGHLIGHTS: 'SET_CITATION_HIGHLIGHTS',
  
  // Connection
  SET_CONNECTION_STATUS: 'SET_CONNECTION_STATUS',
  SET_CONNECTION_ERROR: 'SET_CONNECTION_ERROR',
};

// Reducer function
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_DOCUMENTS:
      return { ...state, documents: action.payload, documentsError: null };
    
    case ActionTypes.SET_DOCUMENTS_LOADING:
      return { ...state, documentsLoading: action.payload };
    
    case ActionTypes.SET_DOCUMENTS_ERROR:
      return { ...state, documentsError: action.payload, documentsLoading: false };
    
    case ActionTypes.ADD_DOCUMENT:
      return { ...state, documents: [...state.documents, action.payload] };
    
    case ActionTypes.REMOVE_DOCUMENT:
      return { 
        ...state, 
        documents: state.documents.filter(doc => doc.filename !== action.payload) 
      };
    
    case ActionTypes.ADD_MESSAGE:
      return { ...state, messages: [...state.messages, action.payload] };
    
    case ActionTypes.UPDATE_MESSAGE:
      return {
        ...state,
        messages: state.messages.map(msg => 
          msg.id === action.payload.id ? { ...msg, ...action.payload.updates } : msg
        )
      };
    
    case ActionTypes.CLEAR_MESSAGES:
      return { ...state, messages: [initialState.messages[0]] };
    
    case ActionTypes.SET_CURRENT_QUERY:
      return { ...state, currentQuery: action.payload };
    
    case ActionTypes.SET_IS_QUERYING:
      return { ...state, isQuerying: action.payload };
    
    case ActionTypes.SET_QUERY_ERROR:
      return { ...state, queryError: action.payload, isQuerying: false };
    
    case ActionTypes.SET_UPLOAD_PROGRESS:
      return { ...state, uploadProgress: action.payload };
    
    case ActionTypes.SET_IS_UPLOADING:
      return { ...state, isUploading: action.payload };
    
    case ActionTypes.SET_UPLOAD_ERROR:
      return { ...state, uploadError: action.payload, isUploading: false };
    
    case ActionTypes.SET_PDF_DATA:
      return { ...state, currentPDFData: action.payload };
    
    case ActionTypes.SET_PDF_VIEWER_MODE:
      return { ...state, pdfViewerMode: action.payload };
    
    case ActionTypes.SET_ACTIVE_CITATION:
      return { ...state, activeCitation: action.payload };
    
    case ActionTypes.SET_CITATION_HIGHLIGHTS:
      return { ...state, citationHighlights: action.payload };
    
    case ActionTypes.SET_CONNECTION_STATUS:
      return { ...state, isConnected: action.payload };
    
    case ActionTypes.SET_CONNECTION_ERROR:
      return { ...state, connectionError: action.payload };
    
    default:
      return state;
  }
}

// Create context
const AppContext = createContext();

// Context provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions
  const actions = {
    // Document actions
    async loadDocuments() {
      dispatch({ type: ActionTypes.SET_DOCUMENTS_LOADING, payload: true });
      try {
        const documents = await apiService.getDocuments();
        dispatch({ type: ActionTypes.SET_DOCUMENTS, payload: documents });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_DOCUMENTS_ERROR, payload: error.message });
        toast.error('Failed to load documents');
      } finally {
        dispatch({ type: ActionTypes.SET_DOCUMENTS_LOADING, payload: false });
      }
    },

    async uploadDocuments(files) {
      dispatch({ type: ActionTypes.SET_IS_UPLOADING, payload: true });
      dispatch({ type: ActionTypes.SET_UPLOAD_PROGRESS, payload: 0 });
      
      try {
        const result = await apiService.uploadDocuments(files);
        dispatch({ type: ActionTypes.SET_UPLOAD_PROGRESS, payload: 100 });
        
        // Reload documents after upload
        await actions.loadDocuments();
        
        toast.success(`Successfully uploaded ${result.documents_processed} documents`);
        return result;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_UPLOAD_ERROR, payload: error.message });
        toast.error('Failed to upload documents');
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_IS_UPLOADING, payload: false });
      }
    },

    async clearDocuments() {
      try {
        await apiService.clearDocuments();
        dispatch({ type: ActionTypes.SET_DOCUMENTS, payload: [] });
        dispatch({ type: ActionTypes.CLEAR_MESSAGES });
        toast.success('All documents cleared');
      } catch (error) {
        toast.error('Failed to clear documents');
        throw error;
      }
    },

    // Message actions
    addMessage(message) {
      const newMessage = {
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString(),
        ...message,
      };
      dispatch({ type: ActionTypes.ADD_MESSAGE, payload: newMessage });
      return newMessage;
    },

    updateMessage(id, updates) {
      dispatch({ type: ActionTypes.UPDATE_MESSAGE, payload: { id, updates } });
    },

    // Query actions
    async queryDocuments(query) {
      if (!query.trim()) return;

      dispatch({ type: ActionTypes.SET_CURRENT_QUERY, payload: query });
      dispatch({ type: ActionTypes.SET_IS_QUERYING, payload: true });
      
      // Add user message
      const userMessage = actions.addMessage({
        type: 'user',
        content: query,
      });

      // Add loading bot message
      const loadingMessage = actions.addMessage({
        type: 'bot',
        content: 'Analyzing your documents...',
        isLoading: true,
      });

      try {
        const result = await apiService.queryDocuments(query);
        
        // Update loading message with actual response
        actions.updateMessage(loadingMessage.id, {
          content: result.response_text,
          isLoading: false,
          citations: result.citations,
          enhancedCitations: result.enhanced_citations,
          htmlContent: result.html_response_with_tooltips,
        });

        return result;
      } catch (error) {
        actions.updateMessage(loadingMessage.id, {
          content: 'Sorry, I encountered an error while analyzing your documents. Please try again.',
          isLoading: false,
          error: true,
        });
        
        dispatch({ type: ActionTypes.SET_QUERY_ERROR, payload: error.message });
        toast.error('Query failed');
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_IS_QUERYING, payload: false });
      }
    },

    // PDF Viewer actions
    async loadPDFData(filename) {
      try {
        const pdfData = await apiService.getDocumentBase64(filename);
        dispatch({ type: ActionTypes.SET_PDF_DATA, payload: pdfData });
        return pdfData;
      } catch (error) {
        toast.error('Failed to load PDF');
        throw error;
      }
    },

    setPDFViewerMode(mode) {
      dispatch({ type: ActionTypes.SET_PDF_VIEWER_MODE, payload: mode });
    },

    // Citation actions
    setActiveCitation(citation) {
      dispatch({ type: ActionTypes.SET_ACTIVE_CITATION, payload: citation });
    },

    setCitationHighlights(highlights) {
      dispatch({ type: ActionTypes.SET_CITATION_HIGHLIGHTS, payload: highlights });
    },

    // Connection actions
    async checkConnection() {
      try {
        await apiService.healthCheck();
        dispatch({ type: ActionTypes.SET_CONNECTION_STATUS, payload: true });
        dispatch({ type: ActionTypes.SET_CONNECTION_ERROR, payload: null });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_CONNECTION_STATUS, payload: false });
        dispatch({ type: ActionTypes.SET_CONNECTION_ERROR, payload: error.message });
      }
    },
  };

  // Check connection on mount
  useEffect(() => {
    actions.checkConnection();
    actions.loadDocuments();
  }, []);

  const value = {
    state,
    actions,
    dispatch,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext; 