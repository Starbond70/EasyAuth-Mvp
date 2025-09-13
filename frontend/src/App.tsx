import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import Header from './components/Header';
import { ExtractedCredential, OCRResponse } from './types';

function App() {
  const [extractionResult, setExtractionResult] = useState<OCRResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = (result: OCRResponse) => {
    setExtractionResult(result);
    setError(null);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setExtractionResult(null);
  };

  const handleReset = () => {
    setExtractionResult(null);
    setError(null);
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {!extractionResult && !error && (
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Extract Academic Credentials
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Upload a certificate (PDF or image) and our advanced OCR system will extract 
              key credential information including name, degree, institution, and more.
            </p>
          </div>
        )}
        
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error processing file
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
                    onClick={handleReset}
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {!extractionResult && (
          <FileUpload
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )}
        
        {extractionResult && (
          <ResultsDisplay 
            result={extractionResult} 
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
}

export default App;
