import fitz  # PyMuPDF
import os
import csv
import re
from pathlib import Path
from collections import defaultdict
import pdf_toc_utils

SKIP_STRINGS = {'DiMaio’s Forensic Pathology', 'Medicolegal Death Investigation'}


def sanitize_for_path(text):
    # Replace problematic characters for file/folder names
    if not isinstance(text, str) or not text:
        return 'unknown'
    text = text.replace('"', '').replace('/', '_').replace('\\', '_').replace(':', '_')
    return text.strip()


def build_image_path(base_path, chapter, section, image_counter):
    # Construct path like: base/images/chapter/section/imageX.png
    chapter = sanitize_for_path(chapter)
    section = sanitize_for_path(section)
    image_filename = f'image{image_counter}.png'
    return Path(base_path) / 'images' / chapter / section / image_filename


def extract_multimodal_data_from_pdf_safe(pdf_path, export_base_path, toc_lines, page_start=0, page_end=None):
    os.makedirs(export_base_path, exist_ok=True)
    os.makedirs(os.path.join(export_base_path, 'images'), exist_ok=True)

    doc = fitz.open(pdf_path)
    start = page_start or 0
    end = page_end if page_end is not None else len(doc)

    toc_entries = pdf_toc_utils.parse_two_line_toc(toc_lines)
    chapter_image_counter = defaultdict(int)
    csv_output = []

    for page_num in range(start, end):
        page = doc[page_num]
        hierarchy = pdf_toc_utils.get_hierarchy_for_page(page_num, toc_entries)
        chapter = hierarchy.get('chapter', 'unknown')
        section = hierarchy.get('section', 'unknown')

        text_blocks = page.get_text('blocks')  # type: ignore
        text_blocks = sorted(text_blocks, key=lambda b: b[1])  # Sort by vertical position

        images = page.get_images(full=True)
        for _, img in enumerate(images, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image['image']
            chapter_image_counter[(chapter, section)] += 1
            image_index = chapter_image_counter[(chapter, section)]
            image_path = build_image_path(export_base_path, chapter, section, image_index)
            image_path.parent.mkdir(parents=True, exist_ok=True)

            with open(image_path, 'wb') as f:
                f.write(image_bytes)

            # Look for figure caption
            caption_text = ''
            for block in text_blocks:
                if re.match(r'^Figure\s+\d+\.\d+', block[4]):
                    caption_text = block[4].strip()
                    break

            csv_output.append({
                'figure_path': str(image_path.relative_to(export_base_path)),
                'caption_text': caption_text,
                'chapter_title': chapter,
                'section_title': section,
            })

    # Write CSV output
    csv_file_path = os.path.join(export_base_path, 'captions.csv')
    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_output[0].keys())
        writer.writeheader()
        writer.writerows(csv_output)

    return csv_file_path, len(csv_output)


# Example usage
if __name__ == '__main__':
    atlas = 'atlas.pdf'
    export_path = './data'
    toc_lines = pdf_toc_utils.extract_toc_lines(atlas)
    example_csv, example_count = extract_multimodal_data_from_pdf_safe(pdf_path=atlas, export_base_path=export_path, toc_lines=toc_lines)
    print(f"\n✅ Extracted {example_count} images and metadata to: {example_csv}")


    