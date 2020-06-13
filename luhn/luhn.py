import os
import sys
from collections import OrderedDict

def luhn__algorithm_checksum(card_to_validate):
    print('Credit Card: {} ({} digits)'.format(card_to_validate, len(card_to_validate)) )

    # Cast the input as string and strip the last digit for checksum. Last digit will be recasted to integer    
    last_digit = int(card_to_validate[-1])
    card_to_validate = card_to_validate[:-1]
    print('Sequence of Credit Card to validate:', card_to_validate)
    print('Last Digit to check against:', last_digit)
    print('Length of the number to validate:', len(card_to_validate))
    print("------------------------------------------------------------------------------------")
    # Cast as int every char digit
    card_to_validate = [ int(number) for number in card_to_validate ]
    print('Sequence   ', card_to_validate)

    # Reverse the order of the number to start from the leftmost
    card_to_validate = card_to_validate[::-1]
    print('Reversed   ', card_to_validate)

    # Double the value of every second digit
    for i in range(0, len(card_to_validate), 2):
        doubled_digit = card_to_validate[i] * 2        
        # If the doubled digit is greater than 9, subtract 9
        if doubled_digit > 9:
            card_to_validate[i] = doubled_digit - 9
        else:
            card_to_validate[i] = doubled_digit
    print('2nd doubled', card_to_validate)

    # We sum all the values together
    sum = 0
    for i in card_to_validate:
        sum += i        

    # Multiply them by 9
    multiplied_sum = sum * 9
    print("2nd doubled sum is {} multiplied by {} equals {}".format(sum, 9, multiplied_sum))

    # Calculate the final check digit
    ckeck_digit = multiplied_sum % 10
    print("Check Digit is multiplied sum {} modulo {} that equals to {}".format(multiplied_sum, 10, ckeck_digit) )
    print("------------------------------------------------------------------------------------")

    if ckeck_digit == last_digit:
        print('Credit Card Validated')
    else:
        print('Credit Card NOT Validated')
    print("------------------------------------------------------------------------------------")



def issuer_identifier(number_to_identify):
    # Create a dict that contains the card issuer's major industry.
    # Raw table found at https://en.wikipedia.org/wiki/ISO/IEC_7812
    MII = {
        '0': 'ISO/TC 68 and other industry assignments',
        '1': 'Airlines',
        '2': 'Airlines, financial and other future industry assignments',
        '3': 'Travel and entertainment',
        '4': 'Banking and financial',
        '5': 'Banking and financial',
        '6': 'Merchandising and banking/financial',
        '7': 'Petroleum and other future industry assignments',
        '8': 'Healthcare, telecommunications and other future industry assignments',
        '9': 'For assignment by national standards bodies'
    }   

    # IIN is defined with this guide for 16 digits length and Actives only: https://en.wikipedia.org/wiki/Payment_card_number
    # There are conflicts in IIN ranges like Diners Club United States & Canada and Mastercard 
    # because Diners Club United States & Canada starts with 2 digits 54, 55 and Mastercard cards range is 2 digits between 51 and 55.
    # Because this is problem of the database i found on wiki, i simply change the range of Mastercard between 51 and 53.

    # Create a dict that contains the Issuer starting numbers of popular cards
    IIN = {
        ('62', '81'): 'China UnionPay',        
        ('54', '55'): 'Diners Club United States & Canada',
        ('36', tuple(range(300, (305+1))), '3095', '38', '39'): 'Diners Club International',
        ('6011', tuple(range(622126, (622925+1))), tuple(range(624000, (626999+1))), tuple(range(628200, (628899+1))), '64', '65'): 'Discover Card',
        ('60', '6521', '6522'): 'RuPay',
        ('636'): 'InterPayment',
        (tuple(range(637, (639+1)))): 'InstaPayment',
        (tuple(range(3528, (3589+1)))): 'JCB',
        ('6759', '676770', '676774'): 'Maestro UK',
        ('50', tuple(range(56, (69+1)))): 'Maestro',
        ('5019', '4571'): 'Dankort',
        (tuple(range(2200, (2204+1)))): 'MIR',
        (tuple(range(6054740, (6054744+1)))): 'NPS Pridnestrovie',
        (tuple(range(2221, (2720+1))), tuple(range(51, (53+1)))): 'Mastercard',
        (tuple(range(979200, (979289+1)))): 'Troy',
        ('4'): 'VISA',
        (tuple(range(506099, (506198+1))), tuple(range(650002, (650027+1)))): 'Verve',
        '357111': 'LankaPay'
    } 

    _dict = {}
    _dict2 = {}

    # Raw table with IIN ranges
    # The purpose of this dictionary manipulation is to create a dictionary in the form of:
    # identifier length: { identifier: Issuer }
    # where identifier length is the length of the number to check if the card starts with (like 650002) which i want to check first in order
    # to identify possible partnerships of big brands like VISA or MasterCard. I will check in a descending order, first identifiers with the 
    # most digits, last identifiers with 2 or single digits.
    # Idintifier is the actual identifier, which will contain the brand (like VISA)
    # In order to achieve values that can be sorted, i need to unpack every tuple into strings and then cast them to integers.
    # I need also to cast simple string keys to integers because i want the dictionary to have the following types:
    # integer: { integer: string }
    # Reminder that a dict's row is an item that contains a key and value (which are iteratables)
    for item in IIN.items():
        if isinstance(item[0], tuple):
            for key in item[0]:
                if isinstance(key, tuple):
                    for nested_key in key:
                        if len(str(nested_key)) in _dict.keys():
                            _dict[len(str(nested_key))].update( {nested_key: item[1]} )
                        else:
                            _dict.update( {len(str(nested_key)): {nested_key: item[1]} } )
                else:
                    if len(str(key)) in _dict.keys():
                        _dict[len(str(key))].update( {int(key): item[1]} )
                    else:
                        _dict.update( {len(str(key)): {int(key): item[1]} } )
        else:
            if len(item[0]) in _dict.keys():
                _dict[len(item[0])].update( {int(item[0]): item[1]} )
            else:
                _dict.update( {len(item[0]): {int(item[0]): item[1]} } )


    # Sort the length of identifiers values in descending order (like: { 6: { 123456: VISA } })
    _dict = OrderedDict(reversed(sorted(_dict.items())))

    # Now i will pass the nested dictionaries in a new dictionary in the form of: { 123456: VISA }
    [ _dict2.update(item_value.items()) for item_value in _dict.values() ]

    # I will sort the new keys in descending order. So now i have a simple dictionary sorted by identifier's length 
    # and then sorted by identifier's value
    _dict2 = OrderedDict(reversed(sorted(_dict2.items())))

    # Finally, if the identifier matches the first numbers of the card, then we have a result.
    # Save the identifier for printing purposes
    identifier_length = 0
    identifier_issuer = ""

    for item in _dict2.items():
        if number_to_identify.startswith(str(item[0])):
            #print(item[0], item[1])
            identifier_issuer = item[1]
            identifier_length = len(str(item[0]))
            break


    # Save the 1st number of the card and issuers
    major_industry_digit = number_to_identify[0]
    issuer_digits = number_to_identify[0:identifier_length]

    issuer_major_industry = ""

    # If first number of the card is found in the dict keys, then we have a result (the value of the item of this key)
    for key in MII.keys():
        if major_industry_digit in key:
            issuer_major_industry = MII[key]

    # The rest of the digits minus the last check digit, belong to the card owner. If the issuer identfier has less than 6 digits, 
    # then we assume that the first 6 digits belongs to the issuer
    if identifier_length < 6:
        identifier_length = 6
    owner_digits = number_to_identify[identifier_length:-1]
    
    print('Major Industry identifier (MII): {} ({})'.format( issuer_major_industry, major_industry_digit))
    print('Issuer Identification Number (IIN): {} ({})'.format(identifier_issuer, issuer_digits))
    print('Individual Account Identifier:', owner_digits)


# Clearing cli for raw input
if sys.platform.startswith('linux'):
    try:
        os.system('clear')
    except:
        pass
elif sys.platform.startswith('win32'):
    try:
        os.system('cls')
    except:
        pass


while(1):
    print("------------------------------------------------------------------------------------")
    print("Enter a choice:\n1.Card Validation\n2.Exit")
    print("------------------------------------------------------------------------------------")
    choice = str(input())
    if choice == '1':
        print("Insert your Credit Card Identification Number to validate: ")
        # Convert the card number to string for easy number manipulation and identification
        card_input = str(input())
        # Check card length in order to accept 16 digits only
        if len(card_input) == 16:
            luhn__algorithm_checksum(card_input)
            issuer_identifier(card_input)
            break
        else:
            print("Cannot validate a Credit Card with more or less than 16 digits")
    elif choice == '2':
        print("Exiting...")
        break
