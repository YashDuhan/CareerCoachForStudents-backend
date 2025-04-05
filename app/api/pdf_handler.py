import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF file"""
    text = ""
    # Create a PDF document from bytes
    pdf_document = fitz.open("pdf", pdf_bytes)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    return text
