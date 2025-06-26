import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppProvider } from './contexts/AppContext';
import MainInterface from './components/MainInterface';
import PDFViewer from './components/PDFViewer';
import './index.css';

function App() {
  return (
    <AppProvider>
    <Router>
        <div className="App min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<MainInterface />} />
          <Route path="/pdf-viewer" element={<PDFViewer />} />
        </Routes>
          
          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                theme: {
                  primary: 'green',
                  secondary: 'black',
                },
              },
            }}
          />
      </div>
    </Router>
    </AppProvider>
  );
}

export default App; 