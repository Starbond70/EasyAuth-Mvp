export interface ExtractedCredential {
  name?: string;
  roll_number?: string;
  degree?: string;
  issue_year?: string;
  institution?: string;
  grade?: string;
  specialization?: string;
  certificate_number?: string;
  raw_text?: string;
  confidence_score?: number;
}

export interface OCRResponse {
  status: string;
  file_id: string;
  original_filename: string;
  extracted_data: ExtractedCredential;
  timestamp: string;
}

export interface UploadProps {
  onUploadComplete: (result: OCRResponse) => void;
  onUploadError: (error: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export interface ResultsProps {
  result: OCRResponse;
  onReset: () => void;
}