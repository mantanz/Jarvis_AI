import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainInterface from './components/MainInterface';
import PDFViewer from './components/PDFViewer';
import './index.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<MainInterface />} />
          <Route path="/pdf-viewer" element={<PDFViewer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 