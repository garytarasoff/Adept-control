import PyPDF2
import sys

def search_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    if 'floppy' in page_text.lower() or 'load' in page_text.lower() or 'drive' in page_text.lower():
                        print(f"--- Page {i+1} ---")
                        lines = page_text.split('\n')
                        for line in lines:
                            if 'floppy' in line.lower() or 'load' in line.lower() or 'drive' in line.lower():
                                print(line)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    search_pdf(sys.argv[1])
