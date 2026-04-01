import React, { useState, useRef } from 'react';
import { uploadPdf } from '../../api/research';

export const UploadPanel: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadMessage(null);

    try {
      const response = await uploadPdf(file);
      setUploadMessage(response.message);
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('An error occurred during upload.');
      }
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="bg-[#1c1c1e] border border-gray-800 rounded-xl p-6 mb-6">
      <h3 className="text-lg font-medium text-white mb-2">Upload Knowledge</h3>
      <p className="text-sm text-gray-400 mb-4">
        Upload a text-based PDF to securely ingest it into the local database.
      </p>
      
      <div className="flex flex-col items-start gap-4">
        <input 
          type="file"
          accept=".pdf"
          className="hidden" 
          ref={fileInputRef}
          onChange={handleFileChange}
        />
        
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          {isUploading ? 'Ingesting PDF...' : 'Select PDF'}
        </button>

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded-lg w-full border border-red-900/50">
            {error}
          </div>
        )}

        {uploadMessage && (
          <div className="text-emerald-400 text-sm bg-emerald-900/20 p-3 rounded-lg w-full border border-emerald-900/50">
            {uploadMessage}
          </div>
        )}
      </div>
    </div>
  );
};
