import fitz
from PIL import Image
import io, re
import pandas as pd


def extract_toc(file_path: str, start: int = 0, end: int = 20):
    '''
    Extract a hierarchical Table of Contents from a PDF.
    Returns a list of entries with levels: chapter, section, subsection.
    '''
    pdf_file = fitz.open(file_path)
    toc_text = ""

    for page_index in range(start, end):
        page = pdf_file.load_page(page_index)
        text = page.get_text()  # type: ignore

        if 'Table of Contents' in text:
            toc_text += text
        elif toc_text:
            toc_text += "\n" + text
            if 'Index' in text or 'Appendix' in text:
                break

    normalized = normalize_toc_text(toc_text)
    toc_entries = extract_hierarchical_toc(normalized)
    return toc_entries



def normalize_toc_text(raw_text: str):
    '''
    Joins lines that are part of the same ToC entry into a single line.
    '''
    lines = raw_text.splitlines()
    normalized_lines = []
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # If the line looks like a TOC entry (starts with a number and ends with a page number)
        if re.match(r'^\d+(\.\d+)*\s+[A-Za-z].*\s+\d+$', line):
            normalized_lines.append(line)
        else:
            if buffer:
                buffer[-1] += " " + line
            else:
                buffer.append(line)

    return "\n".join(normalized_lines)




def extract_hierarchical_toc(text: str):
    '''
    Extracts a hierarchical ToC (chapters, sections, subsections) using regex.
    Returns a list of dicts with level, title, and page number.
    '''
    lines = text.splitlines()
    toc_entries = []
    last_chapter = last_section = None

    pattern = r'^\s*(\d+(?:\.\d+){0,2})\s+([A-Za-z][\w\s,\-–&]+?)\s+(\d{1,4})$'
    for line in lines:
        match = re.match(pattern, line)
        if not match:
            continue

        num_str, title, page = match.groups()
        level = num_str.count('.') + 1
        entry = {
            "number": num_str,
            "title": title.strip(),
            "page": int(page)
        }

        if level == 1:
            entry["level"] = "chapter"
            last_chapter = entry
        elif level == 2:
            entry["level"] = "section"
            entry["parent"] = last_chapter["title"] if last_chapter else None
            last_section = entry
        elif level == 3:
            entry["level"] = "subsection"
            entry["parent"] = last_section["title"] if last_section else (last_chapter["title"] if last_chapter else None)
        
        toc_entries.append(entry)

    return toc_entries


def get_hierarchy_for_page(page_num: int, toc_entries: list[dict]):
    '''
    Returns the deepest matching hierarchy (chapter, section, subsection) for a given page.
    '''
    sorted_entries = sorted(toc_entries, key=lambda e: e["page"])
    current_chapter = current_section = current_subsection = None

    for entry in sorted_entries:
        if page_num >= entry["page"]:
            if entry["level"] == "chapter":
                current_chapter = entry["title"]
                current_section = current_subsection = None
            elif entry["level"] == "section":
                current_section = entry["title"]
                current_subsection = None
            elif entry["level"] == "subsection":
                current_subsection = entry["title"]
        else:
            break

    return {
        "chapter": current_chapter,
        "section": current_section,
        "subsection": current_subsection
    }

