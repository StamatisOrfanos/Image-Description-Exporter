import fitz
from PIL import Image
import io, re
import pandas as pd


def normalize_toc_text(raw_text: str):
    '''
    Joins lines that are part of the same ToC entry into a single line.
    Args:
        raw_test (str): String input of the text provided by the PyMuPDF library
    '''
    lines = raw_text.splitlines()
    normalized_lines = []
    buffer = []

    for line in lines:
        line = line.strip()
        if not line: continue

        # If the line is just a number (possible chapter number or page), buffer it
        if re.fullmatch(r'\d+', line):
            buffer.append(line)
        else:
            # If line has actual content (words), attach to buffer
            if buffer:
                buffer.append(line)
                if len(buffer) >= 3:
                    normalized_lines.append(' '.join(buffer))
                    buffer = []
            else:
                buffer.append(line)

    # Catch any trailing entry
    if len(buffer) >= 3:
        normalized_lines.append(' '.join(buffer))

    return '\n'.join(normalized_lines)


def extract_chapters_from_toc(text: str):
    '''
    Extracts chapters using a regex after normalization.
    Args:
        text (str): A normalized string input for the original text by PyMuPDF
    '''
    pattern = r'\b(\d{1,2})\s+([A-Z][A-Za-z0-9,\-–&\s]+?)\s+(\d{1,4})\b'
    matches = re.findall(pattern, text)
    chapters = []
    for number, title, page in matches:
        chapters.append((title.strip(), int(page)))
    return chapters


def extract_toc(file_path, start=0, end=20):
    pdf_file = fitz.open(file_path)
    toc_text = ""

    for page_index in range(start, end):
        page = pdf_file.load_page(page_index)
        text = page.get_text() # type: ignore
        if 'Table of Contents' in text:
            toc_text += text
        elif toc_text:
            toc_text += "\n" + text
            if 'Index' in text:
                break

    normalized = normalize_toc_text(toc_text)
    chapters = extract_chapters_from_toc(normalized)
    result = {key: value for key, value in chapters}
    return result