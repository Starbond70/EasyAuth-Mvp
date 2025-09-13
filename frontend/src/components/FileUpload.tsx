import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { CloudArrowUpIcon, DocumentIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { UploadProps, OCRResponse } from '../types';

const FileUpload: React.FC<UploadProps> = ({ 
  onUploadComplete, 
  onUploadError, 
  isLoading, 
  setIsLoading 
}) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post<OCRResponse>(
        'http://localhost:8000/extract-text',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 60 seconds timeout
        }
      );
      
      onUploadComplete(response.data);
    } catch (error: any) {
      console.error('Upload error:', error);
      if (error.response) {
        onUploadError(error.response.data.detail || 'Server error occurred');
      } else if (error.request) {
        onUploadError('Unable to connect to server. Please check if the backend is running.');
      } else {
        onUploadError('Upload failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [onUploadComplete, onUploadError, setIsLoading]);
  
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    acceptedFiles,
    fileRejections
  } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: isLoading
  });
  
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive && !isDragReject
            ? 'border-primary-400 bg-primary-50'
            : isDragReject
            ? 'border-red-400 bg-red-50'
            : 'border-gray-300 bg-white hover:border-primary-400 hover:bg-primary-50'
        } ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">Processing...</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Extracting credential information from your document
                </p>
              </div>
            </>
          ) : (
            <>
              {isDragReject ? (
                <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
              ) : (
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400" />
              )}
              
              <div className="text-center">
                {isDragActive && !isDragReject ? (
                  <>
                    <h3 className="text-lg font-medium text-primary-900">
                      Drop your certificate here
                    </h3>
                    <p className="text-sm text-primary-600 mt-1">
                      Release to start processing
                    </p>
                  </>
                ) : isDragReject ? (
                  <>
                    <h3 className="text-lg font-medium text-red-900">
                      Invalid file type
                    </h3>
                    <p className="text-sm text-red-600 mt-1">
                      Please upload a PDF or image file
                    </p>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-medium text-gray-900">
                      Drop your certificate here, or click to browse
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Supports PDF, JPG, PNG, TIFF, BMP (max 10MB)
                    </p>
                  </>
                )}
              </div>
              
              {!isDragActive && (
                <button
                  type="button"
                  className="inline-flex items-center px-4 py-2 border border-primary-300 text-sm font-medium rounded-md text-primary-700 bg-white hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  <DocumentIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                  Choose File
                </button>
              )}
            </>
          )}
        </div>
      </div>
      
      {fileRejections.length > 0 && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-red-800">Upload Error:</h4>
          <ul className="mt-2 text-sm text-red-700">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                {file.name}: {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;