import PyPDF2
import sys

def extract_text(pdf_path, out_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for i, page in enumerate(reader.pages):
                text += f"\n--- Page {i+1} ---\n"
                text += page.extract_text()
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        extract_text(sys.argv[1], sys.argv[2])
    else:
        print("Please provide PDF path and output path")
