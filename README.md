# Spanish Text OCR Extractor

A Python-based OCR (Optical Character Recognition) tool designed to extract Spanish text from images with advanced preprocessing capabilities.

## Features

- Image preprocessing for optimal text recognition
- Spanish language OCR using Tesseract
- Automatic noise and separator line removal
- Support for JPG, JPEG, and PNG formats
- Debug image output for verification
- Text post-processing and cleanup

## Requirements

- Python 3.x
- Tesseract OCR with Spanish language support
- OpenCV
- Pillow (PIL)
- NumPy

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pi-pico
```

2. Install system dependencies (Arch Linux):
```bash
sudo pacman -S tesseract tesseract-data-spa python-opencv python-pip python-numpy
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your images in the `imgs/` directory
2. Run the script:
```bash
python extract_text.py
```

The script will:
- Process all images in the `imgs/` directory
- Save preprocessed images in `debug_images/`
- Save extracted text in `extracted_text/`

## Project Structure

```
.
├── imgs/               # Input images
├── debug_images/       # Preprocessed images (for debugging)
├── extracted_text/     # Extracted text output
├── extract_text.py     # Main script
└── requirements.txt    # Python dependencies
```

## Features in Detail

- **Image Preprocessing**:
  - Contrast enhancement
  - Noise reduction
  - Adaptive thresholding
  - Edge preservation
  - Resolution optimization

- **Text Processing**:
  - Automatic separator line detection
  - Common OCR error correction
  - Spacing and formatting cleanup
  - Special character handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m '[@username][feat:] Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 