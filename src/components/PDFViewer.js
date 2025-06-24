import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  ArrowLeft, 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut,
  FileText,
  Search
} from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';

// Set worker path
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;

const PDFViewer = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const canvasRef = useRef(null);
  const textLayerRef = useRef(null);
  const containerRef = useRef(null);
  
  const [pdfDoc, setPdfDoc] = useState(null);
  const [pageNum, setPageNum] = useState(1);
  const [pageCount, setPageCount] = useState(0);
  const [scale, setScale] = useState(1.2);
  const [loading, setLoading] = useState(true);
  const [chunks, setChunks] = useState([]);
  const [activeChunk, setActiveChunk] = useState('');
  const [filename, setFilename] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const file = params.get('file');
    const chunksData = params.get('chunks');
    const active = params.get('active');
    const fileData = params.get('fileData');

    if (file) {
      setFilename(file);
    }

    if (chunksData) {
      try {
        const parsedChunks = JSON.parse(decodeURIComponent(chunksData));
        setChunks(parsedChunks);
      } catch (error) {
        console.error('Error parsing chunks:', error);
      }
    }

    if (active) {
      setActiveChunk(active);
    }

    // Load actual PDF file
    if (fileData) {
      try {
        const fileBlob = new Blob([new Uint8Array(JSON.parse(fileData))], { type: 'application/pdf' });
        loadPDFFromFile(fileBlob);
      } catch (error) {
        console.error('Error creating file from data:', error);
      }
    }
  }, [location]);

  const loadPDFFromFile = async (file) => {
    try {
      setLoading(true);
      
      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = pdfjsLib.getDocument(arrayBuffer);
      const pdf = await loadingTask.promise;
      
      setPdfDoc(pdf);
      setPageCount(pdf.numPages);
      setLoading(false);
      
      // Render first page
      renderPage(1);
      
    } catch (error) {
      console.error('Error loading PDF:', error);
      setLoading(false);
    }
  };

  const renderPage = async (num) => {
    if (!pdfDoc) return;

    try {
      const page = await pdfDoc.getPage(num);
      const viewport = page.getViewport({ scale: scale });
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.height = viewport.height;
      canvas.width = viewport.width;

      // Render PDF page on canvas
      const renderContext = {
        canvasContext: context,
        viewport: viewport
      };

      await page.render(renderContext).promise;

      // Create text layer for highlighting
      await createRealTextLayer(page, viewport);

    } catch (error) {
      console.error('Error rendering page:', error);
    }
  };

  const createRealTextLayer = async (page, viewport) => {
    const textLayer = textLayerRef.current;
    if (!textLayer) return;

    textLayer.innerHTML = '';
    textLayer.style.width = `${viewport.width}px`;
    textLayer.style.height = `${viewport.height}px`;
    textLayer.style.left = canvasRef.current.offsetLeft + 'px';
    textLayer.style.top = canvasRef.current.offsetTop + 'px';

    try {
      const textContent = await page.getTextContent();
      
      // Create text spans manually for better control
      textContent.items.forEach((textItem, index) => {
        const span = document.createElement('span');
        span.textContent = textItem.str;
        span.style.position = 'absolute';
        span.style.left = `${textItem.transform[4]}px`;
        span.style.top = `${viewport.height - textItem.transform[5]}px`;
        span.style.fontSize = `${textItem.transform[0]}px`;
        span.style.fontFamily = textItem.fontName || 'Arial';
        span.style.color = 'transparent';
        span.style.whiteSpace = 'pre';
        span.style.transformOrigin = '0% 0%';
        textLayer.appendChild(span);
      });

    } catch (error) {
      console.error('Error creating text layer:', error);
    }
  };

  const highlightChunk = (chunkId) => {
    const chunk = chunks.find(c => `chunk-${c.source_num}` === chunkId);
    if (!chunk) return;

    // Clear previous highlights
    const spans = textLayerRef.current?.querySelectorAll('span');
    spans?.forEach(span => {
      span.classList.remove('highlight');
      span.style.background = '';
      span.style.border = '';
      span.style.borderRadius = '';
      span.style.boxShadow = '';
      span.style.display = '';
      span.style.padding = '';
      span.style.marginLeft = '';
    });

    // Get the full text content
    let fullText = chunk.tooltip_text || chunk.content || '';
    if (!fullText.trim()) return;

    // Extract first 5 and last 5 words from the chunk
    const words = fullText.split(/\s+/).filter(word => word.length > 0);
    if (words.length < 3) return;

    const firstWords = words.slice(0, Math.min(5, words.length)).join(' ').toLowerCase();
    const lastWords = words.slice(-Math.min(5, words.length)).join(' ').toLowerCase();

    // Build continuous text from spans to match against
    let continuousText = '';
    let spanTextMap = [];

    spans?.forEach((span, index) => {
      const spanText = span.textContent || '';
      spanTextMap.push({
        span: span,
        text: spanText,
        startIndex: continuousText.length,
        endIndex: continuousText.length + spanText.length
      });
      continuousText += spanText + ' ';
    });

    const continuousTextLower = continuousText.toLowerCase();

    // Find the positions of first and last word sequences
    let startPos = continuousTextLower.indexOf(firstWords);
    let endPos = continuousTextLower.lastIndexOf(lastWords);

    // If exact match fails, try partial matches
    if (startPos === -1) {
      for (let i = Math.min(3, words.length); i >= 1; i--) {
        const partialFirst = words.slice(0, i).join(' ').toLowerCase();
        startPos = continuousTextLower.indexOf(partialFirst);
        if (startPos !== -1) break;
      }
    }

    if (endPos === -1 || endPos <= startPos) {
      for (let i = Math.min(3, words.length); i >= 1; i--) {
        const partialLast = words.slice(-i).join(' ').toLowerCase();
        const tempPos = continuousTextLower.lastIndexOf(partialLast);
        if (tempPos !== -1 && tempPos > startPos) {
          endPos = tempPos + partialLast.length;
          break;
        }
      }
    }

    if (startPos === -1 || endPos === -1 || endPos <= startPos) return;

    // Highlight all spans that fall within the identified text region
    let firstHighlight = null;
    spanTextMap.forEach(spanInfo => {
      if (spanInfo.endIndex > startPos && spanInfo.startIndex < endPos) {
        spanInfo.span.classList.add('highlight');
        spanInfo.span.style.background = 'rgba(255, 193, 7, 0.7)';
        spanInfo.span.style.border = '2px solid #ff9800';
        spanInfo.span.style.borderRadius = '6px';
        spanInfo.span.style.boxShadow = '0 0 10px rgba(255, 152, 0, 0.5)';
        spanInfo.span.style.display = 'inline-block';
        spanInfo.span.style.padding = '2px 4px';
        spanInfo.span.style.marginLeft = '-2px';

        if (!firstHighlight) {
          firstHighlight = spanInfo.span;
        }
      }
    });

    // Scroll to first highlight
    if (firstHighlight) {
      setTimeout(() => {
        firstHighlight.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }, 300);
    }
  };

  const navigateToChunk = (chunkId) => {
    const chunk = chunks.find(c => `chunk-${c.source_num}` === chunkId);
    if (!chunk) return;

    setActiveChunk(chunkId);
    
    if (chunk.page !== pageNum) {
      setPageNum(chunk.page);
    }

    setTimeout(() => {
      highlightChunk(chunkId);
    }, 300);
  };

  const nextPage = () => {
    if (pageNum < pageCount) {
      setPageNum(pageNum + 1);
    }
  };

  const prevPage = () => {
    if (pageNum > 1) {
      setPageNum(pageNum - 1);
    }
  };

  const zoomIn = () => {
    setScale(prev => Math.min(prev + 0.2, 3.0));
  };

  const zoomOut = () => {
    setScale(prev => Math.max(prev - 0.2, 0.5));
  };

  useEffect(() => {
    if (pdfDoc && !loading) {
      renderPage(pageNum);
    }
  }, [scale, pageNum, loading, pdfDoc]);

  useEffect(() => {
    if (activeChunk && chunks.length > 0) {
      setTimeout(() => {
        highlightChunk(activeChunk);
      }, 500);
    }
  }, [activeChunk, chunks]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar - Citation Sources */}
      <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-blue-600 hover:text-blue-800 font-medium mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Chat
          </button>
          <h2 className="text-lg font-semibold text-gray-800 mb-2">📚 Citation Sources</h2>
          <p className="text-sm text-gray-600">
            {chunks.length} source{chunks.length !== 1 ? 's' : ''} found
          </p>
        </div>

        <div className="space-y-3">
          {chunks.map((chunk) => {
            const chunkId = `chunk-${chunk.source_num}`;
            const isActive = activeChunk === chunkId;
            
            return (
              <div
                key={chunkId}
                className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                  isActive 
                    ? 'bg-orange-50 border-orange-300 shadow-md' 
                    : 'bg-gray-50 border-gray-200 hover:bg-blue-50 hover:border-blue-300'
                }`}
                onClick={() => navigateToChunk(chunkId)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-blue-600">
                    Source {chunk.source_num}
                  </span>
                  <span className="text-xs text-gray-500">
                    Page {chunk.page}
                  </span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-3">
                  {chunk.tooltip_text || chunk.content}
                </p>
              </div>
            );
          })}
        </div>

        {chunks.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No citation sources available</p>
          </div>
        )}
      </div>

      {/* Main PDF Viewer */}
      <div className="flex-1 flex flex-col">
        {/* Header Controls */}
        <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={prevPage}
              disabled={pageNum <= 1}
              className="flex items-center px-3 py-2 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-800 disabled:opacity-50 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Prev
            </button>
            
            <button
              onClick={nextPage}
              disabled={pageNum >= pageCount}
              className="flex items-center px-3 py-2 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-800 disabled:opacity-50 rounded-lg transition-colors"
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </button>

            <div className="flex items-center space-x-2">
              <span>Page:</span>
              <input
                type="number"
                min="1"
                max={pageCount}
                value={pageNum}
                onChange={(e) => setPageNum(Math.max(1, Math.min(pageCount, parseInt(e.target.value) || 1)))}
                className="w-16 px-2 py-1 text-black rounded text-center"
              />
              <span>of {pageCount}</span>
            </div>

            <button
              onClick={zoomIn}
              className="flex items-center px-3 py-2 bg-blue-700 hover:bg-blue-800 rounded-lg transition-colors"
            >
              <ZoomIn className="w-4 h-4 mr-1" />
              Zoom In
            </button>

            <button
              onClick={zoomOut}
              className="flex items-center px-3 py-2 bg-blue-700 hover:bg-blue-800 rounded-lg transition-colors"
            >
              <ZoomOut className="w-4 h-4 mr-1" />
              Zoom Out
            </button>
          </div>

          <h1 className="text-lg font-semibold">
            📄 {filename || 'Document Viewer'}
          </h1>
        </div>

        {/* PDF Canvas Container */}
        <div className="flex-1 overflow-auto bg-gray-100 p-8">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading PDF...</p>
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <div 
                ref={containerRef}
                className="relative bg-white shadow-lg"
                style={{ width: `${595 * scale}px`, height: `${842 * scale}px` }}
              >
                <canvas
                  ref={canvasRef}
                  className="block"
                  style={{ width: `${595 * scale}px`, height: `${842 * scale}px` }}
                />
                <div
                  ref={textLayerRef}
                  className="textLayer"
                  style={{ 
                    width: `${595 * scale}px`, 
                    height: `${842 * scale}px`,
                    position: 'absolute',
                    top: 0,
                    left: 0
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PDFViewer; 