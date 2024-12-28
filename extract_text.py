import pytesseract
from PIL import Image, ImageEnhance
import os
import cv2
import numpy as np
from pathlib import Path

print("Script started...")

# Set the path to the directory containing images
image_directory = './imgs'

def enhance_image_pil(image):
    # Convert to PIL Image if needed
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)
    
    return image

def preprocess_image(image):
    print("Preprocessing image...")
    # Convert PIL image to OpenCV format
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Resize image while maintaining aspect ratio
    height, width = image.shape[:2]
    target_width = 2500
    if width != target_width:
        scale = target_width / width
        dim = (target_width, int(height * scale))
        image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to remove noise while preserving edges
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,  # Block size
        2    # Constant
    )
    
    # Convert back to PIL Image and enhance
    pil_image = Image.fromarray(thresh)
    enhanced = enhance_image_pil(pil_image)
    
    print("Preprocessing complete")
    return enhanced

def is_separator_line(line: str) -> bool:
    # Check if line is likely a separator (contains mostly special characters)
    special_chars = set('«»€¢£¥§©®™²³¹¼½¾×÷~@#$%^&*+=<>{}[]|\\/')
    char_count = len(line)
    special_count = sum(1 for c in line if c in special_chars or c.isupper())
    return char_count > 0 and (special_count / char_count) > 0.3

def extract_text_from_image(image_path: str) -> tuple[str, str]:
    try:
        print(f"Processing {image_path}...")
        # Open the image
        image = Image.open(image_path)
        
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Save processed image for debugging
        debug_dir = Path('debug_images')
        debug_dir.mkdir(exist_ok=True)
        processed_image.save(debug_dir / f"processed_{Path(image_path).name}")
        
        print("Extracting text...")
        # Extract text using Spanish language with optimized configuration
        custom_config = r'--oem 3 --psm 6 -l spa'
        text = pytesseract.image_to_string(
            processed_image,
            lang='spa',
            config=custom_config
        )
        
        # Enhanced post-processing
        text = text.replace('\n\n', '\n')  # Remove double line breaks
        text = text.replace('|', 'l')      # Common OCR mistake
        text = text.replace('1.', '1.')    # Fix numbered lists
        text = text.replace('2.', '2.')
        text = text.replace('3.', '3.')
        text = text.replace('4.', '4.')
        text = text.replace('5.', '5.')
        
        # Clean up lines and remove separators
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not is_separator_line(line):  # Skip empty lines and separators
                # Fix common OCR mistakes
                line = line.replace('  ', ' ')  # Remove double spaces
                line = line.replace(' .', '.')
                line = line.replace(' ,', ',')
                lines.append(line)
        
        text = '\n'.join(lines)
        print("Text extraction complete")
        
        return Path(image_path).name, text
    except Exception as e:
        print(f"Error: {str(e)}")
        return Path(image_path).name, f"Error processing {image_path}: {str(e)}"

def main():
    print("Starting main function...")
    # Create output directory if it doesn't exist
    output_dir = Path('extracted_text')
    output_dir.mkdir(exist_ok=True)
    
    # Get all image paths
    image_paths = [
        os.path.join(image_directory, f) 
        for f in sorted(os.listdir(image_directory)) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    
    print(f"Found {len(image_paths)} images")
    
    # Process images sequentially
    results = [extract_text_from_image(path) for path in image_paths]
    
    # Save and display results
    for filename, text in results:
        print(f"\nProcessing {filename}...")
        
        # Save to file
        output_file = output_dir / f"{Path(filename).stem}_text.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Text extracted from {filename}:")
        print("-" * 50)
        print(text)
        print("-" * 50)

if __name__ == "__main__":
    main() 