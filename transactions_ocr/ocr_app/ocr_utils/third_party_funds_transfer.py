import re

def extract_info_from_string_funds_transfer(raw_text):
    substring = 'OTHER PAYMENT DETAILS'
    starting_index = raw_text.find(substring)
    ending_index = starting_index + len(substring) - 1
    ending_index

    second_substring= 'RECEIPT NUMBER'
    starting_index2 = raw_text.find(second_substring)
    #raw_text = raw_text.replace('\n','')
    keys_string = raw_text[starting_index2:ending_index]
    values_string = raw_text[ending_index+1:].replace('Make another transfer\n','')

    keys = keys_string.split('\n')
    values = values_string.split('\n')

    # Removing empty strings from the lists
    keys = [key.strip(':') for key in keys if key != '']
    values = [value for value in values if value != '']

    # Creating a dictionary by zipping the keys and values together
    data_dict = dict(zip(keys, values))

    # Printing the dictionary
    print(data_dict)

    substring = 'Step 3of3'
    status = raw_text[raw_text.find(substring)+len(substring):raw_text.find('HISTORY')].replace('\n','')

    info_dict = {
        "SenderBankName": None,
        "SenderAccountNumber": data_dict.get('ACCOUNT TO BE TRANSFERRED FROM', None),
        "RecipientBankName": data_dict.get('BANK NAME', None),
        "RecipientName": data_dict.get('RECIPIENT NAME', None),
        "RecipientAccountNumber": data_dict.get('RECEIPT NUMBER', None),
        "TransferType": None,
        "TransferMethod":  data_dict.get('PAYMENT METHOD', None),
        "PaymentType": data_dict.get('PAYMENT TYPE', None),
        "Amount": data_dict.get('AMOUNT', None),
        "RecipientReference": data_dict.get('RECIPIENT REFERENCE', None),
        "OtherPaymentDetails": data_dict.get('(OTHER PAYMENT DETAIL', None),
        "ReferenceNumber": data_dict.get('RECEIPT NUMBER', None),
        "TransactionDateTime": data_dict.get('WHEN TO BE TRANSFERRED', None),
        "Status": status,
        "DuitNowReferenceNumber":data_dict.get('DUITNOW REFERENCE NO',None),
        "DuitNowCharges": data_dict.get('DUITNOW CHARGES',None),
        "ServiceCharge": data_dict.get('SERVICE CHARGE',None),
        "TotalAmount": data_dict.get('TOTAL AMOUNT',None),
        "WhenToTransfer":  data_dict.get('WHEN TO BE TRANSFERRED', None)
    }

    return info_dict