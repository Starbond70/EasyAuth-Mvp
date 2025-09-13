# Academic Credential OCR System

A secure web-based system for authenticating academic credentials using advanced Deep OCR technology. This MVP focuses on extracting credential information from certificates and diplomas using state-of-the-art OCR engines.

## 🎯 Project Overview

This system aims to build a comprehensive platform for academic credential verification. The current MVP delivers the Deep OCR extraction feature, with future versions planned to include blockchain verification, forgery detection, and digital watermarking.

### Long-term Vision
- **Admin Portal**: Upload certificates via CSV (new) or scanned documents (legacy)
- **System Core**: Extract data, validate via blockchain, detect tampering
- **Verification Interface**: Real-time certificate authenticity verification
- **Advanced Features**: QR codes, digital watermarking, audit logs, AI-powered forgery detection

### Current MVP Features
- 🔍 **Deep OCR Extraction**: Advanced text extraction from certificates and diplomas
- 📄 **Multi-format Support**: PDF and image file processing (JPG, PNG, TIFF, BMP)
- 🧠 **Smart Field Recognition**: Automatic extraction of structured credential data
- 💾 **Data Storage**: SQLite database for extraction records
- 🌐 **Modern Web Interface**: React-based responsive UI
- 📊 **JSON Export**: Download extracted data in JSON format

## 🏗️ Architecture

```
academic-credential-ocr/
├── backend/          # FastAPI backend with OCR service
├── frontend/         # React TypeScript frontend
├── uploads/          # File upload storage
├── database/         # SQLite database files
└── docs/            # Additional documentation
```

### Tech Stack

**Backend:**
- **FastAPI**: High-performance web framework
- **EasyOCR**: Deep learning-based OCR engine
- **PyMuPDF**: Advanced PDF processing
- **SQLite**: Lightweight database
- **OpenCV**: Image preprocessing

**Frontend:**
- **React**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client for API calls
- **React Dropzone**: File upload interface

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```


3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install all required packages, including **SQLAlchemy** (needed for database support). If you see a `ModuleNotFoundError: No module named 'sqlalchemy'`, make sure to re-run the above command inside your virtual environment.
   
   **Important:** If you encounter an error about `PIL.Image` and `ANTIALIAS`, downgrade Pillow to 9.5.0:
   ```bash
   pip install pillow==9.5.0
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

   If you see errors about Tailwind CSS and PostCSS, make sure your `postcss.config.js` contains:
   ```js
   module.exports = {
     plugins: [
       require('tailwindcss'),
       require('autoprefixer'),
     ],
   };
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## 📖 Usage Guide

### Web Interface

1. **Open your browser** and navigate to `http://localhost:3000`
2. **Upload a certificate** by:
   - Dragging and dropping the file onto the upload area
   - Clicking "Choose File" to browse your computer
3. **Wait for processing** - the system will extract credential information
4. **Review the results** displaying structured fields like:
   - Student Name
   - Roll Number
   - Degree/Qualification
   - Institution
   - Year of Issue
   - Grade/CGPA
   - And more...
5. **Download results** as JSON for further processing

### Supported File Types

- **PDF Documents**: Both text-based and scanned PDFs
- **Image Formats**: JPG, JPEG, PNG, TIFF, BMP
- **File Size Limit**: 10MB maximum

### API Endpoints

#### Extract Text from Document
```http
POST /extract-text
Content-Type: multipart/form-data

Parameters:
- file: Certificate file (PDF or image)
```

**Response:**
```json
{
  "status": "success",
  "file_id": "uuid-string",
  "original_filename": "certificate.pdf",
  "extracted_data": {
    "name": "John Doe",
    "roll_number": "CS2021001",
    "degree": "Bachelor of Computer Science",
    "institution": "University of Technology",
    "issue_year": "2024",
    "grade": "First Class",
    "confidence_score": 0.92
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Get All Extractions
```http
GET /extractions
```

#### Get Specific Extraction
```http
GET /extractions/{file_id}
```

## 🔧 Configuration

### Backend Configuration

The backend can be configured by modifying `backend/main.py`:

- **Server Host/Port**: Change uvicorn.run() parameters
- **CORS Origins**: Modify CORS middleware settings
- **Upload Directory**: Adjust UPLOAD_DIR path
- **Database Path**: Configure database location in `Database` class

### OCR Settings

OCR performance can be tuned in `backend/ocr_service.py`:

- **Language Support**: Modify EasyOCR Reader languages
- **GPU Usage**: Enable GPU acceleration if available
- **Image Preprocessing**: Adjust OpenCV parameters
- **Extraction Patterns**: Customize regex patterns for different credential formats

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📊 Performance Notes

### OCR Accuracy Factors
- **Image Quality**: Higher resolution images yield better results
- **Text Clarity**: Clean, high-contrast text improves extraction
- **Document Layout**: Standard certificate layouts work best
- **Language**: Currently optimized for English text

### Processing Time
- **Images**: 2-5 seconds depending on size and complexity
- **PDFs**: 1-3 seconds for text-based, 3-8 seconds for scanned
- **Large Files**: Processing time scales with file size

## 🔮 Future Roadmap

### Version 2.0 - Blockchain Integration
- Ethereum-based credential verification
- Smart contracts for certificate validation
- Immutable credential records

### Version 3.0 - Security Features
- AI-powered forgery detection
- Digital watermarking
- Tamper evidence algorithms

### Version 4.0 - Enterprise Features
- Multi-tenant architecture
- Advanced audit logging
- Batch processing capabilities
- REST API rate limiting

## 🐛 Troubleshooting

### Common Issues

**1. Backend fails to start:**
- Ensure Python 3.8+ is installed
- Check virtual environment activation
- Verify all dependencies are installed

**2. OCR extraction returns empty results:**
- Check image quality and resolution
- Ensure text is clearly visible
- Try different file formats

**3. Frontend cannot connect to backend:**
- Verify backend is running on port 8000
- Check CORS configuration
- Ensure firewall allows local connections

**4. File upload fails:**
- Check file size (max 10MB)
- Verify file format is supported
- Ensure sufficient disk space


### Debug Mode & Troubleshooting

**Common Issues Fixed in This Version:**
- Pillow 10+ breaks some OCR dependencies. Downgrade to Pillow 9.5.0 if you see `ANTIALIAS` errors.
- Tailwind CSS/PostCSS plugin errors: use the config above and update all related packages to latest.
- Clear `__pycache__` if you see persistent Python errors after upgrades.

Enable debug logging in the backend by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **EasyOCR** team for the excellent OCR engine
- **FastAPI** community for the robust web framework
- **React** team for the powerful frontend library
- **Tailwind CSS** for the beautiful styling system

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Built with ❤️ for secure academic credential verification**