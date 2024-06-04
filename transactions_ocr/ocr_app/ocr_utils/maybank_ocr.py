import re
import os
import cv2
import pytesseract
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

MODEL="gpt-3.5-turbo-0301"


input_string = 'DuitNow Transfer\\n\\nReference ID\\n\\n192560425M\\n\\nBeneficiary name\\n\\nFEDERAL STAT&PUBL CO S/B\\n\\nBeneficiary account number\\n\\n3209 1007 03\\n\\nReceiving bank\\n\\nPUBLIC BANK\\n\\nRecipient reference\\n\\n‘CW + caymen hee + 5K\\n\\nAmount\\n\\nRM 110.40\\n\\nMalayan Banking Berhad (Co. Reg.\\n\\n196001000142)\\n\\nMaybank Islamic Berhad (Co. Reg. : 20070102941)\\n\\n \\n\\nful\\n\\n \\n\\x0c'

prompt = f"""
Given a input string '{input_string}', the task is to extract key value pairs. 
Find the list of keys ['Reference ID', 'status','Beneficiary name', 'Beneficiary account number', 'Receiving bank', 'Recipient reference',
                         Payment Details,'Amount']
and there corresponding values.

Return a dictionary containing the extracted key-value pairs. Do not write python code.

Example 1:
  Given the input string 
  DuitNow Transfer\\n\\nReference ID\\n\\n192560425M\\n\\nBeneficiary name\\n\\nFEDERAL STAT&PUBL CO S/B\\n\\nBeneficiary account number\\n\\n3209 1007 03\\n\\nReceiving bank\\n\\nPUBLIC BANK\\n\\nRecipient reference\\n\\n‘CW + caymen hee + 5K\\n\\nAmount\\n\\nRM 110.40\\n\\nMalayan Banking Berhad (Co. Reg.\\n\\n196001000142)\\n\\nMaybank Islamic Berhad (Co. Reg. : 20070102941)\\n\\n \\n\\nful\\n\\n \\n\\x0c
  the output look like this:


  Extract the following key-value pairs:

  {{
      'Reference ID': '192560425M',
      'Beneficiary name': 'FEDERAL STAT&PUBL CO S/B',
      'Beneficiary account number': '3209 1007 03',
      'Receiving bank': 'PUBLIC BANK',
      'Recipient reference': '‘CW + caymen hee + 5K',
      'Amount': 'RM 110.40'
  }}

Example 2:
  Given the input string 
  'Favourite 3rd Party Transfer\n\n \n\nStatus: ‘Successful\nReference Number: 4950560438\n\nTransaction Date: 04 Dec 2023 20:\n\n‘Amount: RM100.00\n\nTo Favourite 3rd Party Account 014114420912\n\n‘Account Holder Name PIBG SRJK (C) CHOONG\nRecipient Reference Chin Kai Yin 5K\n\nOther Transfer Details Nov &Dec 2023\n\nNote: This receipt is computer generated and no signature is required.\n\n‘Malayan Banking Berhad (Co. Rep: 8600100182 | Maybank mi Berhad (Co. Rep: 200701029811)\n\x0c'
  the output look like this:


  Extract the following key-value pairs:

  {{
      'Reference ID': '4950560438',
      'Beneficiary name': 'PIBG SRJK (C) CHOONG',
      'Beneficiary account number': '014114420912',
      'Receiving bank': 'To Favourite 3rd Party Account',
      'Recipient reference': '‘Chin Kai Yin 5K',
      'Amount': 'RM 100.00',
      'Status':'Successful'
  }}

Example 3:
  Given the input string 
  'Favourite 3rd Party Transfer\n\nStatus:\nReference Number:\nTransaction Date:\n\n‘Amount:\n\nTo Favourite Sid Party Account\n‘Account Holder Name\nRecipient Reference\n\n(Other Transfer Details\n\nSuccessful\n4950560438\n04 Dec 2023 20:\n\nRM100.00\n\n014114420912\nPIBG SRUK (C) CHOONG\nChin Kai Yin 5K\nNov &Dec 2023\n\nNote: This receipt is computer generated and no signature is required.\n\n‘Malayan Banking Berhad (Co. Rep: 18600100182 | Maybank mi Berhad (Co. Rep: 200701029811)\n'
  the output look like this:


  Extract the following key-value pairs:

  {{
      'Reference ID': '4950560438',
      'Beneficiary name': 'PIBG SRJK (C) CHOONG',
      'Beneficiary account number': '014114420912',
      'Receiving bank': 'To Favourite 3rd Party Account',
      'Recipient reference': '‘Chin Kai Yin 5K',
      'Amount': 'RM 100.00',
      'Status':'Successful'
  }}
"""

def getChatResponseStr(prompt,input_string) :
    """
    Function to generate a chat response based on the prompt and user input.

    Args:
    - prompt: The prompt to be used for chat generation
    - user_input: The input from the user

    Returns:
    - The generated chat response
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": input_string}  # Including user input in the messages
            ],
            temperature = 0
        )
        return {'response':completion, 'msg':'Success'}
    except Exception as e:
        return  {'response':None, 'msg':str(e)}

def find_nth_occurrence(string, substring, n):
    start = 0
    for i in range(n):
        index = string.find(substring, start)
        if index == -1:
            return -1
        start = index + 1
    return index

def extract_date_time(image):
  gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # Enhance contrast using histogram equalization
  equalized_image = cv2.equalizeHist(gray_image)

  text = pytesseract.image_to_string(equalized_image)

  date_time_str = None
  # Sample string
  #text = """\n\nReference.|D\n»849887115M\n\n“38 Mar 2024, 2:00 PM\n\nBereticidty Hams\nANDREW JYE & col\n\nBeneficiary account number\n28881 0578 04977\n\nReceiving barik:\n\nRetipieht reterarice\nSng lip seng esi"\n\nPayment details\nStrata title.\n\nAmount,\n\nRM.4,500.00\n\nTiss\n\n  \n\nIs computet.genetated and no\n\n   \n\x0c"""

  # Regular expression to match date and time in the format "38 Mar 2024, 2:00 PM"
#   pattern = r'\b(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4},\s\d{1,2}:\d{2}\s(?:AM|PM))\b'
  pattern = r'\d{1,2}\s[A-Z][a-zA-Z]{2}\s\d{4},\s\d{1,2}:\d{2}\s(?:AM|PM)'
  # Extract date and time
  matches = re.findall(pattern, text)

  # If matches are found, convert to datetime object
  if matches:
      date_time_str = matches[0]
  return date_time_str


# Function to extract text from image using OCR
def extract_text_from_image(image_path):
    # img = Image.open(image_path)
    # Read the image
    image = cv2.imread(str(image_path))

    # Display the image
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    date_time_str = extract_date_time(image)
    text = pytesseract.image_to_string(img)
    return text, date_time_str

def extract_info_from_text(text, date_time_str, bank_name):
    print(repr(text))

    data_dict = {}
    rslt = getChatResponseStr(prompt,text)
    if rslt['response']:
        response_message = rslt["response"].choices[0].message.content
        data_dict = eval(response_message)

    status = 'Successful'

    # Construct dictionary with extracted information
    info_dict = {
        "SenderBankName": bank_name,
        "SenderAccountNumber": None,
        "RecipientBankName":data_dict.get('Receiving bank',None),
        "RecipientName": data_dict.get('Beneficiary name',None),
        "RecipientAccountNumber": data_dict.get('Beneficiary account number',None),
        "TransferType": None,
        "TransferMethod": None,
        "PaymentType": None,
        "Amount": data_dict.get('Amount',None),
        "RecipientReference": data_dict.get('Recipient reference',None),
        "OtherPaymentDetails": data_dict.get('Payment details',None),
        "ReferenceNumber": data_dict.get('Reference ID',None),
        "TransactionDateTime": date_time_str,
        "Status": status,
        "DuitNowReferenceNumber":None,
        "DuitNowCharges": None,
        "ServiceCharge": None,
        "TotalAmount": None,
        "WhenToTransfer": None
    }

    return info_dict


def extract_info_from_text_v2(text, bank_name):

    # Define regular expressions to extract information
    status_pattern = r'Status:\s*‘?(.*?)\n'
    reference_number_pattern = r'Reference Number:\s*(.*?)\n'
    transaction_date_pattern = r'Transaction Date:\s*(.*?)\n'
    amount_pattern = r'Amount:\s*(.*?)\n'
    account_pattern = r'To Favourite 3rd Party Account\s*(.*?)\n'
    account_holder_pattern = r'Account Holder Name\s*(.*?)\n'
    recipient_reference_pattern = r'Recipient Reference\s*(.*?)\n'

    # Extract information using regular expressions
    status = re.search(status_pattern, text).group(1)
    reference_number = re.search(reference_number_pattern, text).group(1)
    transaction_date = re.search(transaction_date_pattern, text).group(1)
    amount = re.search(amount_pattern, text).group(1)
    receiving_bank = re.search(account_pattern, text).group(1)
    account_holder_name = re.search(account_holder_pattern, text).group(1)
    recipient_reference = re.search(recipient_reference_pattern, text).group(1)

    # Construct dictionary with extracted information
    info_dict = {
        "SenderBankName": bank_name,
        "SenderAccountNumber": None,
        "RecipientBankName":'To Favourite 3rd Party Account',
        "RecipientName": account_holder_name,
        "RecipientAccountNumber": receiving_bank,
        "TransferType": None,
        "TransferMethod": None,
        "PaymentType": None,
        "Amount": amount,
        "RecipientReference": recipient_reference,
        "OtherPaymentDetails": None,
        "ReferenceNumber": reference_number,
        "TransactionDateTime": transaction_date,
        "Status": status,
        "DuitNowReferenceNumber":None,
        "DuitNowCharges": None,
        "ServiceCharge": None,
        "TotalAmount": None,
        "WhenToTransfer": None
    }

    return info_dict