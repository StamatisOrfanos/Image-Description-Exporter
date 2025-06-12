import os

import fitz


def extract_images_labels(file_path: str, export_path: str, page_start: int = 0, page_end: int = None): # type: ignore
    '''
    Create a dataset using the images and labels of a certain pdf file
    Args:
        file_path (str): local path to the pdf document
        page_start (int): page number to start the process
        page_end (int): page number to end the process
        export_path (str): local path to export the data 
    '''
    # Create the export directory if it does not exist
    os.makedirs(export_path, exist_ok=True)
    
    # Read document and provide the range of pages to process 
    all_images = []
    pdf_file = fitz.open(file_path)
    start = 0 if page_start is None else page_start
    end   = len(pdf_file) if page_end is None else min(page_end, len(pdf_file))
    
    # Get chapters titles and pages per chapter for correct mapping of images
    # chapters_dict = extract_toc(file_path, start, end)
    
    for page_index in range(end):
        if page_index < start: continue
        page = pdf_file.load_page(page_index)
        image_list = page.get_images(full=True)
        if not image_list: continue
        
        for image_index, img in enumerate(image_list, start=1):
            # XREF of the image, extract the image bytes and get the image extension 
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image['image']
            image_ext = base_image['ext']
            
            # Get the rectangle area around the image
            # image_rect = find_image_rect_by_xref(page, xref)
            # if image_rect is None:
            #     continue


            
            # Get the chapter the image is under so that we name them better
            # image_chapter = get_chapter_for_page(page_index, chapters_dict)

            # Save the image
            # image_name = f'{export_path}/images/{image_chapter}/{image_index}.{image_ext}'
            # all_images.append(image_name)
            # with open(image_name, 'wb') as image_file:
            #     image_file.write(image_bytes)
            #     # print(f'[+] Image saved as {image_name}')