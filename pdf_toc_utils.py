import fitz  # PyMuPDF
import re
import pandas as pd

def extract_toc_lines(pdf_path, start=0, end=20):
    pdf_file = fitz.open(pdf_path)
    toc_text = ''

    for page_index in range(start, end):
        page = pdf_file.load_page(page_index)
        text = page.get_text()  # type: ignore

        if 'Contents' in text and not toc_text:
            toc_text += text
        elif toc_text:
            toc_text += '\n' + text
            if 'Index' in text or 'Appendix' in text:
                break

    return toc_text.splitlines()


def parse_two_line_toc(lines, toc_page_offset=15):
    toc_entries = []
    current_chapter = None
    i = 0

    while i < len(lines) - 1:
        first_line = lines[i].strip()
        second_line = lines[i + 1].strip()

        # Detect a chapter: line with number, followed by title
        if re.fullmatch(r"\d+", first_line) and second_line:
            current_chapter = f"{first_line} {second_line}"
            toc_entries.append({
                'level': 'chapter',
                'title': current_chapter,
                'page': None  # will be filled by first section page
            })
            i += 2
        # Detect section: title followed by a page number
        elif re.fullmatch(r"\d+", second_line) and current_chapter:
            page = int(second_line) + toc_page_offset
            toc_entries.append({
                'level': 'section',
                'title': first_line,
                'page': page,
                'parent': current_chapter
            })
            # Update chapter page if not set
            for entry in reversed(toc_entries):
                if entry['level'] == 'chapter' and entry['title'] == current_chapter and entry['page'] is None:
                    entry['page'] = page
                    break
            i += 2
        else:
            i += 1

    return sorted(toc_entries, key=lambda x: x['page'] or 0)


def get_hierarchy_for_page(page_num: int, toc_entries: list[dict]):
    sorted_entries = sorted(toc_entries, key=lambda e: e['page'] or 0)
    current_chapter = None
    current_section = None

    for entry in sorted_entries:
        if page_num >= entry['page']:
            if entry['level'] == 'chapter':
                current_chapter = entry['title']
                current_section = None
            elif entry['level'] == 'section':
                current_section = entry['title']
        else:
            break

    return {
        'chapter': current_chapter,
        'section': current_section
    }



# Run the script directly to test on a sample TOC PDF
if __name__ == '__main__':
    toc_path = 'atlas.pdf'
    toc_lines = extract_toc_lines(toc_path)
    toc_entries = parse_two_line_toc(toc_lines)

    print("\nParsed TOC entries:")
    for entry in toc_entries:
        print(entry)

    # Test: get the hierarchy for a page
    print("\nSample hierarchy for page 130:")
    print(get_hierarchy_for_page(130, toc_entries))
