def process_md(file_path, search_term, find_first_only=True):
    results = []
    search_lower = search_term.lower()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            if search_lower in line.lower():
                results.append(("Markdown", f"Line {line_num}", line.strip()))
                if find_first_only:
                    break
    return results

def register(registry):
    registry[".md"] = {
        "handler": process_md,
        "name": "Markdown search",
        "description": "Search in Markdown (*.md) files"}