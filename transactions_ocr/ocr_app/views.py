from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileUploadSerializer
import os
import datetime
from pathlib import Path
import cv2
import fitz
from skimage.metrics import structural_similarity
from .utils import match_logo
from .ocr_utils.maybank_ocr import (extract_text_from_image,
                                    extract_info_from_text,
                                    extract_info_from_text_v2)
from .ocr_utils.pb_ocr import extract_info_from_text_pb
from .ocr_utils.third_party_funds_transfer import extract_info_from_string_funds_transfer


def resize_image(image, width, height):
    # Resize the image
    resized_image = cv2.resize(image, (width, height))
    
    return resized_image



def convert_pdf_receipt_to_image(pdf_path):
    rslt = {}
    page_number = 0
    try:
    # Open the PDF file
        #pdf_images = convert_from_path(pdf_path,dpi=500)
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(page_number)

        current_time = datetime.datetime.now()
        date_time_str = current_time.strftime("%Y_%m_%d_%H_%M_%S")
        # temp_image_path = os.path.join('media/temp',f'temp_{date_time_str}.png')
        temp_image_path = Path('media/temp') / f'temp_{date_time_str}.png'
        
        # pdf_images[0].save(temp_image_path, 'PNG') #consider 1st page only
        # Render the page as an image
        pix = page.get_pixmap()
        pix.save(temp_image_path)
    
        rslt ['msg'] = 'pdf converted to image successfully!'
        rslt['file_path'] = temp_image_path
    except Exception as e:
        print(f"Error: {e}")
        rslt ['msg'] = f"Error: {e}"
        rslt['file_path'] = None

    return rslt

def detect_receipt_bank_name(receipt_image_path):
    rslt ={}
    # folder_path = 'static'
    logos_folder_path = 'media/temp/logos/'
    cropped_logo_path = 'media/temp/cropped_temp'
    resized_width,resized_height = 150, 40
    rslt_dict = {}

    try:
        for cropped_image_path in os.listdir(cropped_logo_path):
            # p1 = os.path.join(cropped_logo_path,cropped_image_path)
            p1 = str(Path(cropped_logo_path) / cropped_image_path)
            print(p1)
            receipt_image = cv2.imread(p1)
            resized_receipt_image = resize_image(receipt_image, resized_width, resized_height)


            for filename in os.listdir(logos_folder_path):
                print(filename)
                # Check if the file is an image (assuming jpg format in this example)
                if filename.endswith(".png"):
                    # Construct the full file path
                    # file_path = os.path.join(logos_folder_path, filename)
                    file_path = Path(logos_folder_path) / filename
                    # Read the image using cv2.imread
                    image = cv2.imread(str(file_path))
                    resized_image = resize_image(image, resized_width, resized_height)
                    # Convert images to grayscale
                    first_gray = cv2.cvtColor(resized_receipt_image, cv2.COLOR_BGR2GRAY)
                    second_gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
                    # Compute SSIM between two images
                    score, diff = structural_similarity(first_gray, second_gray, full=True)
                    print("Similarity Score: {:.3f}%".format(score * 100))
                    temp = f'{cropped_image_path}@@@{filename}'
                    rslt_dict[temp] = score * 100

        # sorted_dict = dict(sorted(rslt.items(), key=lambda x: x[1], reverse=True))
        max_key_name = max(rslt_dict, key=lambda k: rslt_dict[k])
        # in ur case the above line is thowing that error ^
        #please pring rslt_dict before it in your code
        #[os.remove(os.path.join(cropped_logo_path, file)) for file in os.listdir(cropped_logo_path) if os.path.isfile(os.path.join(cropped_logo_path, file))]
        [file_path.unlink() for file_path in Path(cropped_logo_path).iterdir() if file_path.is_file()]
        print("Key with maximum value:", max_key_name)
        print(max_key_name.rpartition("@@@")[2].strip('.png'))
        rslt ['msg'] = f"Brand Name found!"
        rslt['bank_name'] = max_key_name.rpartition("@@@")[2].strip('.png')


    except Exception as e:
        print(f"Error: {e}")
        rslt ['msg'] = f"Error: {e}"
        rslt['bank_name'] = None

    return rslt


class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        print(os.listdir('static'))
        info = {}
        if serializer.is_valid():
            file = serializer.validated_data['file']
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff']
            file_extension = os.path.splitext(file.name)[1].lower()[1:]
            if file_extension in allowed_extensions:
                # Save the file
                # file_path = os.path.join('media', file.name)
                file_path = str(Path('media') / file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                if file_extension == 'pdf':
                    print('.pdf')
                    pdf_rslt = convert_pdf_receipt_to_image(file_path)
                    if pdf_rslt['file_path'] is not None:

                        match_logo(pdf_rslt['file_path'])
                        #print(detect_receipt_bank_name(pdf_rslt['file_path']))
                        bank_name_rslt = detect_receipt_bank_name(pdf_rslt['file_path'])
                        # bank_name_rslt={}
                        # bank_name_rslt['bank_name'] = "MayBank"
                        if bank_name_rslt['bank_name'] is not None:
                            print('Bank Name found..',bank_name_rslt['bank_name'] )
                            raw_text, date_time_str = extract_text_from_image(pdf_rslt['file_path'])
                            print(raw_text)
                            print('--------------')
                            print(repr(raw_text))
                            if bank_name_rslt['bank_name'] == 'MayBank':
                                info = extract_info_from_text(raw_text, date_time_str, bank_name_rslt['bank_name'])

                            if bank_name_rslt['bank_name'] == 'PBe':
                                info = extract_info_from_text_pb(raw_text, bank_name_rslt['bank_name'])
                            if bank_name_rslt['bank_name'] == '3rdPartyFundsTransfer':
                                info = extract_info_from_string_funds_transfer(raw_text)

                elif file_extension in ['jpg', 'jpeg', 'png']:
                    print('not pdf')
                    match_logo(file_path)
                    bank_name_rslt = detect_receipt_bank_name(file_path)
                    # bank_name_rslt={}
                    # bank_name_rslt['bank_name'] = "MayBank"
                    if bank_name_rslt['bank_name'] is not None:
                        print('Bank Name found..')
                        raw_text, date_time_str = extract_text_from_image(file_path)
                        print(raw_text)
                        print('--------------')
                        print(bank_name_rslt['bank_name'])
                        if bank_name_rslt['bank_name'] == 'MayBank':
                            info = extract_info_from_text(raw_text,date_time_str, bank_name_rslt['bank_name'])

                        if bank_name_rslt['bank_name'] == 'PBe':
                            info = extract_info_from_text_pb(raw_text, bank_name_rslt['bank_name'])
                        if bank_name_rslt['bank_name'] == '3rdPartyFundsTransfer':
                            info = extract_info_from_string_funds_transfer(raw_text)

                return Response({'Status':'Pass','Ori':'list out all the text read and its value', 'Formatted':info}, status=status.HTTP_201_CREATED)
            else:
                return Response({'Status':'Pass','Ori': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
