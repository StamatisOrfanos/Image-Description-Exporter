import fitz  # PyMuPDF
from PIL import Image
import io, re
import pandas as pd
from pdf_toc_utils import extract_toc

file = 'qrl.pdf'
atlas = 'atlas.pdf'
export_path = '/Users/stamatiosorphanos/Desktop/Image-Description-Exporter'


def extract_images_labels(file_path: str, export_path: str, page_start: int = 0, page_end: int = None): # type: ignore
    '''
    Create a dataset using the images and labels of a certain pdf file
    Args:
        file_path (str): local path to the pdf document
        page_start (int): page number to start the process
        page_end (int): page number to end the process
        export_path (str): local path to export the data 
    '''
    # Read document and provide the range of pages to process 
    all_images = []
    pdf_file = fitz.open(file_path)
    start = 0 if page_start is None else page_start
    end   = len(pdf_file) if page_end is None else min(page_end, len(pdf_file))
    
    # Get chapters titles and pages per chapter for correct mapping of images
    chapters_dict = extract_toc(file_path, start, end)
    
    for page_index in range(end):
        
        if page_index < start: continue
        page = pdf_file.load_page(page_index)
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list, start=1):
            # XREF of the image
            xref = img[0]

            # Extract the image bytes and get the image extension 
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Get the chapter the image is under so that we name them better
            

            # save the image
            image_name = f"{export_path}/image{page_index+1}_{image_index}.{image_ext}"
            all_images.append(image_name)
            # with open(image_name, "wb") as image_file:
            #     image_file.write(image_bytes)
            #     # print(f"[+] Image saved as {image_name}")
        




        
        
    


if __name__ == '__main__':
    # extract_images_labels(file, export_path, 0, 100)
    result = extract_toc(atlas, 0, 10)
