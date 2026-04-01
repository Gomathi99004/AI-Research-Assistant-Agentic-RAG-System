import React, { useState, useRef, DragEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { uploadPdf } from '../../api/research';

export interface UploadPanelProps {
  onUploadSuccess?: () => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Invalid format. Only PDF files are supported.');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadMessage(null);

    try {
      const response = await uploadPdf(file);
      setUploadMessage(response.message);
      if (onUploadSuccess) {
          // Add a tiny artificially premium delay before sliding the panel to let the success state be seen
          setTimeout(() => {
              onUploadSuccess();
          }, 600);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An unexpected error occurred during upload.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full relative group">
      {/* Animated glowing background shadow */}
      <div className={`absolute -inset-0.5 rounded-2xl blur opacity-20 transition duration-1000 group-hover:duration-200 ${
        isDragActive ? 'bg-indigo-500 opacity-50' : 'bg-gradient-to-r from-blue-600 to-indigo-600'
      }`}></div>
      
      <div 
        className={`relative bg-[#1c1c1e] border-2 rounded-2xl min-h-[300px] p-8 flex flex-col items-center justify-center transition-all duration-300 overflow-hidden ${
          isDragActive ? 'border-indigo-500 bg-indigo-500/10' : 'border-zinc-800/80 hover:border-zinc-700/80'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input 
          type="file"
          accept=".pdf"
          className="hidden" 
          ref={fileInputRef}
          onChange={handleChange}
        />

        <AnimatePresence mode="wait">
          {!isUploading && !uploadMessage && !error && (
            <motion.div 
              key="default"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col items-center justify-center w-full"
            >
              <div 
                className={`p-4 rounded-full mb-4 transition-colors duration-300 ${
                  isDragActive ? 'bg-indigo-500/20 text-indigo-400' : 'bg-zinc-800/50 text-zinc-400 group-hover:text-zinc-300'
                }`}
              >
                <UploadCloud className="w-10 h-10" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Upload Knowledge</h3>
              <p className="text-sm text-zinc-400 mb-6 text-center max-w-[280px]">
                Drag and drop your PDF here, or click to browse your files.
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-2.5 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white rounded-xl text-sm font-medium transition-all shadow-lg hover:shadow-xl active:scale-95 flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Select PDF File
              </button>
            </motion.div>
          )}

          {isUploading && (
            <motion.div 
              key="uploading"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center justify-center w-full py-4 relative"
            >
              {/* Premium Scanning Laser Animation */}
              <div className="relative w-16 h-20 bg-zinc-800/50 rounded-lg flex items-center justify-center overflow-hidden mb-6 border border-zinc-700/50 shadow-inner">
                <FileText className="w-8 h-8 text-indigo-400/50" />
                <motion.div 
                  initial={{ top: "-10%" }}
                  animate={{ top: "110%" }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                  className="absolute left-0 w-full h-[2px] bg-indigo-400 shadow-[0_0_12px_3px_rgba(99,102,241,0.8)]"
                />
              </div>

              <h3 className="text-lg font-medium text-white mb-2 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                Ingesting Document...
              </h3>
              <p className="text-xs text-zinc-500 text-center px-4">
                Extracting textual knowledge mathematically for vector search...
              </p>
              
              <div className="w-full max-w-[200px] h-1 bg-zinc-800 rounded-full mt-6 overflow-hidden relative">
                 <motion.div 
                   className="absolute h-full bg-indigo-500 rounded-full w-1/3 shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                   animate={{ left: ["-100%", "200%"] }}
                   transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                 />
              </div>
            </motion.div>
          )}

          {error && !isUploading && (
            <motion.div 
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center w-full py-2"
            >
              <div className="p-3 bg-red-500/10 rounded-full mb-3">
                <AlertCircle className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">Upload Failed</h3>
              <p className="text-sm text-red-400/90 mb-6 text-center max-w-[280px]">
                {error}
              </p>
              <button
                onClick={() => setError(null)}
                className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white rounded-lg text-sm transition-colors"
              >
                Try Again
              </button>
            </motion.div>
          )}

          {uploadMessage && !isUploading && !error && (
            <motion.div 
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center w-full py-2"
            >
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", bounce: 0.5, duration: 0.6 }}
                className="p-3 bg-emerald-500/10 rounded-full mb-4 shadow-[0_0_30px_rgba(16,185,129,0.2)]"
              >
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              </motion.div>
              <h3 className="text-lg font-medium text-white mb-2">Ingestion Complete</h3>
              <p className="text-sm text-emerald-400/80 text-center max-w-[280px]">
                {uploadMessage}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
