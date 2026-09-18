
from pypdf import PdfReader

def read_document(path):
    reader = PdfReader(str(path))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        pages.append({"page_number": number, "text": page.extract_text() or ""})
    return pages
