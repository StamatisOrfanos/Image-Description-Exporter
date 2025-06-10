import fitz
from PIL import Image
import io, re
import pandas as pd


def extract_toc(file_path: str, start: int=0, end: int=20):
    '''
    Extract the Table of Contents including chapter title and starting page
    Args:
        file_path (str): Local path of the file we want to extract the Table of Contents information
        start (int): Page to start the extraction of the images
        end (int): Page to end the extraction of the images
    '''
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
    chapters_dict = {key: value for key, value in chapters}
    result_dict = {key.replace(' ', '_').replace('-', '_').lower(): value for key, value in chapters_dict.items()}
    return result_dict


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



def get_chapter_for_page(page_num, chapter_dict):
    '''
    Gets the chapter that the image belongs to based on the page we find the image
    Args:
        page_num (int): Page number that the image is located at
        chapter_dict (dict): The chapters dictionary that includes the chapters titles and starting page
    '''
    # Convert to list of tuples and sort by starting page
    sorted_chapters = sorted(chapter_dict.items(), key=lambda x: x[1])
    
    current_chapter = None
    for title, start_page in sorted_chapters:
        if page_num >= start_page:
            current_chapter = title
        else:
            break
    return current_chapter