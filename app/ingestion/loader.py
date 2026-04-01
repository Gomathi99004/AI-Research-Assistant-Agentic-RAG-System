import fitz
import io
import time
from typing import List, Dict
from app.core.config import settings

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

if genai and settings.gemini_keys:
    genai.configure(api_key=settings.gemini_keys[0])

def load_pdf(file_path: str) -> List[Dict]:
    docs = []
    doc = fitz.open(file_path)
    
    ocr_model = None
    if genai and settings.gemini_keys:
        ocr_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text().strip()
        images = page.get_images(full=True)
        
        if images and ocr_model and Image:
            print(f"Page {page_num + 1} contains images. Triggering AI OCR for full content extraction...")
            try:
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                prompt = (
                    "Extract all text from this page image exactly as written. Ensure you capture text nested in images, "
                    "diagrams, or tables. "
                )
                if text:
                    prompt += f"For context, here is the raw digital text already found: \n\n{text}\n\nPlease unify and return the complete page text. Do not add conversational filler. If there is no text, return an empty string."
                else:
                    prompt += "Do not add conversational filler. If there is no text, return an empty string."
                    
                response = ocr_model.generate_content([prompt, img])
                time.sleep(4) # Rate limit avoidance
                
                extracted_text = response.text.strip() if response.text else ""
                
                if extracted_text:
                    text = extracted_text
                    print(f"Successfully processed Page {page_num + 1} with AI OCR.")
                else:
                    print(f"AI OCR found no text on Page {page_num + 1}. Using digital text fallback.")
            except Exception as e:
                print(f"AI OCR Failed for Page {page_num + 1}: {e}")
                
        elif not text and not images and ocr_model and Image:
            print(f"Page {page_num + 1} is empty of digital objects. Triggering AI OCR fallback...")
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                response = ocr_model.generate_content(["Extract all text from this image exactly as written. Do not add conversational filler.", img])
                time.sleep(4) # Rate limit avoidance
                extracted = response.text.strip() if response.text else ""
                if extracted:
                    text = extracted
            except Exception as e:
                print(f"AI OCR sweep failed: {e}")
                
        if text:
            docs.append({
                "text": text,
                "page_number": page_num + 1,
                "source_title": file_path.split("/")[-1].split("\\")[-1]
            })
            
    return docs
