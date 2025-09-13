import React from 'react';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Academic Credential OCR
              </h1>
              <p className="text-sm text-gray-500">
                Deep learning-powered certificate extraction
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">MVP Version</p>
              <p className="text-xs text-gray-500">OCR Extraction Only</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
