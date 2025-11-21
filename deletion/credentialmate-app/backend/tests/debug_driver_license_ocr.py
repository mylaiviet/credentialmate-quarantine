"""
Debug script to check OCR extraction from driver's license document.
"""
import sys
import os
from pathlib import Path

# Set environment variables BEFORE any app imports
os.environ[
    "DATABASE_URL"
] = "postgresql://postgres:Welcome2ppms1@localhost:5432/credentialmate"
os.environ["SECRET_KEY"] = "dev-secret-key-for-testing-min-32-chars-required-here"

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
import pytesseract

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Driver's license file path
driver_license_path = (
    Path(__file__).parent.parent.parent
    / ".test_files"
    / "Tricia Drivers License Mo exp 2031.pdf"
)

print(f"Driver's License file path: {driver_license_path}")
print(f"File exists: {driver_license_path.exists()}")

if driver_license_path.exists():
    # Check if it's a PDF
    if driver_license_path.suffix == ".pdf":
        print("\nThis is a PDF file. Converting to image first...")
        import fitz  # PyMuPDF

        # Open PDF
        pdf_doc = fitz.open(driver_license_path)
        page = pdf_doc[0]

        # Render page to image
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")

        # Save as temp image for debugging
        temp_img_path = Path(__file__).parent / "temp_driver_license.png"
        with open(temp_img_path, "wb") as f:
            f.write(img_bytes)

        print(f"Saved temporary image to: {temp_img_path}")

        # Load with PIL
        img = Image.open(temp_img_path)
    else:
        # Load directly
        img = Image.open(driver_license_path)

    # Extract text with Tesseract
    print("\n" + "=" * 80)
    print("OCR EXTRACTED TEXT (raw):")
    print("=" * 80)
    text = pytesseract.image_to_string(img)
    print(text)

    print("\n" + "=" * 80)
    print("OCR EXTRACTED TEXT (uppercase):")
    print("=" * 80)
    text_upper = text.upper()
    print(text_upper)

    # Check for driver license keywords
    driver_keywords = [
        "DRIVER LICENSE",
        "DRIVER'S LICENSE",
        "DRIVERS LICENSE",
        "DEPARTMENT OF MOTOR VEHICLES",
        "DMV",
    ]

    print("\n" + "=" * 80)
    print("KEYWORD SEARCH RESULTS:")
    print("=" * 80)
    for keyword in driver_keywords:
        found = keyword in text_upper
        print(f"  {keyword:40s} : {'✓ FOUND' if found else '✗ NOT FOUND'}")

    matches = sum(1 for keyword in driver_keywords if keyword in text_upper)
    print(f"\nTotal matches: {matches}/5")
    print(f"Pattern matching threshold: 1+ matches")
    print(
        f"Result: {'✓ SHOULD BE DETECTED' if matches >= 1 else '✗ WILL NOT BE DETECTED'}"
    )
else:
    print("ERROR: Driver's license file not found!")
