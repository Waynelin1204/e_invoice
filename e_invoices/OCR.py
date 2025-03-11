from google.cloud import vision
from pdf2image import convert_from_path
import json
import io
import os

client = vision.ImageAnnotatorClient()

def detect_text(file_path):
    result_dict = {}
    
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pdf":
        # Convert PDF to images
        images = convert_from_path(file_path)
    elif file_ext in [".jpg", ".jpeg", ".png"]:
        # Read image file directly
        with open(file_path, "rb") as img_file:
            images = [img_file.read()]
    else:
        print("Unsupported file format. Only PDF, JPG, and PNG are supported.")
        return None

    # Convert PDF to images
    #images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        if file_ext == ".pdf":
	        image_byte_array = io.BytesIO()
	        image.save(image_byte_array, format='PNG')
	        content = image_byte_array.getvalue()
        else:
            content= image

        image = vision.Image(content=content)
        
        try:
            response = client.text_detection(image=image)
        except Exception as e:
            print(f"Error: {e}")
            return

        # Extract texts from the response
        texts = response.text_annotations

        if texts:
            full_text = texts[0].description  # The first item is usually the entire document text
            result_dict["text"] = full_text
        else:
            result_dict["text"] = "No Text"

    return result_dict

# Path to the PDF file
#pdf_path = '/home/pi/Downloads/發票明細(示意圖)_MF57558922_20250303184623865.pdf'

# Get the OCR result
#result_dict = detect_text(pdf_path)

#if result_dict:
    # Convert result to JSON format and print it
#    json_result = json.dumps(result_dict, indent=4, ensure_ascii=False)
#    print(json_result)

    # Save result to a JSON file
#    with open('ocr_result.json', 'w', encoding='utf-8') as json_file:
#        json.dump(result_dict, json_file, ensure_ascii=False, indent=4)
