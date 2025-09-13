import React from 'react';
import { CheckCircleIcon, ArrowDownTrayIcon, ArrowUturnLeftIcon, ClockIcon } from '@heroicons/react/24/outline';
import { ResultsProps } from '../types';

const ResultsDisplay: React.FC<ResultsProps> = ({ result, onReset }) => {
  const { extracted_data, original_filename, timestamp, file_id } = result;
  
  const downloadAsJSON = () => {
    const dataStr = JSON.stringify(result, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `extracted_credentials_${file_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getFieldLabel = (key: string): string => {
    const labels: Record<string, string> = {
      name: 'Student Name',
      roll_number: 'Roll Number',
      degree: 'Degree/Qualification',
      issue_year: 'Year of Issue',
      institution: 'Institution',
      grade: 'Grade/CGPA',
      specialization: 'Specialization',
      certificate_number: 'Certificate Number',
      confidence_score: 'OCR Confidence'
    };
    return labels[key] || key.replace('_', ' ').toUpperCase();
  };

  const renderFieldValue = (key: string, value: any) => {
    if (key === 'confidence_score') {
      const percentage = Math.round((value as number) * 100);
      return (
        <div className="flex items-center">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            percentage >= 80 
              ? 'bg-green-100 text-green-800' 
              : percentage >= 60 
              ? 'bg-yellow-100 text-yellow-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {percentage}%
          </span>
        </div>
      );
    }
    
    if (key === 'raw_text') {
      return null; // Don't display raw text in the main fields
    }
    
    return <span className="text-gray-900 font-medium">{value}</span>;
  };

  // Filter out raw_text and undefined/empty values for the main display
  const displayFields = Object.entries(extracted_data)
    .filter(([key, value]) => key !== 'raw_text' && value !== null && value !== undefined && value !== '')
    .sort(([a], [b]) => {
      // Custom sorting to show important fields first
      const order = ['name', 'roll_number', 'degree', 'institution', 'issue_year', 'grade', 'specialization', 'certificate_number', 'confidence_score'];
      return order.indexOf(a) - order.indexOf(b);
    });

  return (
    <div className="max-w-4xl mx-auto">
      {/* Success Header */}
      <div className="mb-8 text-center">
        <CheckCircleIcon className="mx-auto h-16 w-16 text-green-400" />
        <h2 className="mt-4 text-3xl font-bold text-gray-900">
          Extraction Complete!
        </h2>
        <p className="mt-2 text-lg text-gray-600">
          Successfully extracted credential information from <span className="font-medium">{original_filename}</span>
        </p>
      </div>

      {/* Results Grid */}
      <div className="bg-white shadow-lg rounded-lg overflow-hidden mb-6">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Extracted Credential Information
            </h3>
            <div className="flex items-center text-sm text-gray-500">
              <ClockIcon className="h-4 w-4 mr-1" />
              {formatTimestamp(timestamp)}
            </div>
          </div>
        </div>
        
        <div className="px-6 py-4">
          {displayFields.length > 0 ? (
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {displayFields.map(([key, value]) => (
                <div key={key} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <dt className="text-sm font-medium text-gray-500 mb-1">
                    {getFieldLabel(key)}
                  </dt>
                  <dd className="text-base">
                    {renderFieldValue(key, value)}
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">
                No structured data could be extracted from this document.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Raw Text Section */}
      {extracted_data.raw_text && (
        <div className="bg-white shadow-lg rounded-lg overflow-hidden mb-6">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Raw Extracted Text
            </h3>
          </div>
          <div className="px-6 py-4">
            <div className="bg-gray-50 rounded-md p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {extracted_data.raw_text}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={downloadAsJSON}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <ArrowDownTrayIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          Download as JSON
        </button>
        
        <button
          onClick={onReset}
          className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <ArrowUturnLeftIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          Process Another Document
        </button>
      </div>

      {/* File Info */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          File ID: <span className="font-mono">{file_id}</span>
        </p>
      </div>
    </div>
  );
};

export default ResultsDisplay;