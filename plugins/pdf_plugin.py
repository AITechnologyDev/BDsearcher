import PyPDF2

def handle_pdf(file_path, search_term):
    results = []
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                text = reader.pages[page_num].extract_text()
                if search_term.lower() in text.lower():
                    results.append(("PDF", f"Page {page_num+1}", text[:200] + "..."))
        return results
    except Exception as e:
        return [("Error", "", str(e))]

def register(handlers):
    handlers['.pdf'] = {
        'name': 'PDF Plugin',
        'description': 'Basic PDF text extraction',
        'handler': handle_pdf
    }