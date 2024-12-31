import fitz  # PyMuPDF
import pdfplumber
import json
import os

def extract_images_and_captions_by_topic(pdf_file, output_json, output_dir="static"):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory '{output_dir}' created.")
    else:
        print(f"Output directory '{output_dir}' already exists.")

    data = []  # To store topic-wise image and caption data
    current_topic = None

    # Open PDF with PyMuPDF
    pdf = fitz.open(pdf_file)
    print(f"Opened PDF file: {pdf_file}")

    # Open PDF with pdfplumber for text extraction
    with pdfplumber.open(pdf_file) as pdf_text:
        print("Started extracting pages...")
        for page_number, page in enumerate(pdf_text.pages, start=1):
            print(f"Processing page {page_number}...")

            # Skip front page and index (example: first 2 pages)
            if page_number <= 2:
                print(f"Skipping page {page_number} (front page or index).")
                continue

            # Extract page text
            text = page.extract_text()
            if not text:
                print(f"No text found on page {page_number}.")
                continue

            # Detect topic headings (heuristic: large font or all caps)
            lines = text.split("\n")
            for line in lines:
                if line.isupper():  # Example heuristic for topic headings
                    current_topic = line.strip()
                    data.append({"topic": current_topic, "images": []})
                    print(f"Detected topic: {current_topic}")
                    break

            # Extract images using PyMuPDF
            page_data = {"page": page_number, "images": []}
            for img_index, img in enumerate(pdf[page_number - 1].get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save image to file
                image_filename = f"{output_dir}/page_{page_number}_img_{img_index}.{image_ext}"
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)
                print(f"Saved image: {image_filename}")

                # Attempt to extract captions (nearby text)
                caption = ""
                if lines:
                    caption = lines[0]  # Simplistic heuristic: first line on the page

                # Add image and caption data
                page_data["images"].append({
                    "image_path": image_filename,
                    "caption": caption
                })

            # Add images to the current topic
            if current_topic and page_data["images"]:
                topic_index = next((i for i, t in enumerate(data) if t["topic"] == current_topic), None)
                if topic_index is not None:
                    data[topic_index]["images"].extend(page_data["images"])

    # Write data to JSON file
    with open(output_json, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Extraction complete. Images saved in '{output_dir}', JSON saved as '{output_json}'")

# File paths
pdf_file = "C:/Users/alisa/OneDrive/Desktop/Machine Learning Note/Physicsbook.pdf"  # Replace with your PDF file path
output_json = "Physicsbook.json"  # Output JSON file

# Run the function
extract_images_and_captions_by_topic(pdf_file, output_json)
