import cv2
import pytesseract

import re

# Function to extract text from image using OCR
def extract_text_from_image(image_path):
    # img = Image.open(image_path)
    # Read the image
    image = cv2.imread(image_path)

    # Display the image
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #date_time_str = extract_date_time(image)
    text = pytesseract.image_to_string(img)
    return text


def extract_info_from_text_pb(input_string, bank_name):
    # Define regular expressions to extract information
    reference_number_pattern = r'Reference Number\s+(\d+)'
    amount_pattern = r'Amount\s+RM\s+([\d,]+\.\d{2})'
    transaction_date_pattern = r'Transaction Date / Time\s+(.*?)\n'
    from_account_pattern = r'From Account\s+(.*?)\n'
    recipient_account_pattern = r"Recipient's Account\s+(\d+)"
    recipient_name_pattern = r"Recipient's Name\s+(.*?)\n"
    recipient_bank_pattern = r"Recipient's Bank\s+(.*?)\n"
    recipient_reference_pattern = r"Recipient's Reference\s+(.*?)\n"

    # Extract information using regular expressions
    reference_number = re.search(reference_number_pattern, input_string).group(1)
    amount = re.search(amount_pattern, input_string).group(1)
    transaction_date = re.search(transaction_date_pattern, input_string).group(1)
    from_account = re.search(from_account_pattern, input_string).group(1)
    recipient_account = re.search(recipient_account_pattern, input_string).group(1)
    recipient_name = re.search(recipient_name_pattern, input_string).group(1)
    recipient_bank = re.search(recipient_bank_pattern, input_string).group(1)
    recipient_reference = re.search(recipient_reference_pattern, input_string).group(1)



    info_dict = {
        "SenderBankName": bank_name,
        "SenderAccountNumber": from_account,
        "RecipientBankName": recipient_bank,
        "RecipientName": recipient_name,
        "RecipientAccountNumber": recipient_account,
        "TransferType": None,
        "TransferMethod": None,
        "PaymentType": None,
        "Amount": amount,
        "RecipientReference": recipient_reference,
        "OtherPaymentDetails": None,
        "ReferenceNumber": reference_number,
        "TransactionDateTime": transaction_date,
        "Status": None,
        "DuitNowReferenceNumber":None,
        "DuitNowCharges": None,
        "ServiceCharge": None,
        "TotalAmount": None,
        "WhenToTransfer": None
    }

    return info_dict