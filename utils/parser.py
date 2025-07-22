import re

def extract_debit_amounts(messages):
    amounts = []
    pattern = r"(?:Rs\.?|INR)[ ]?([0-9,]+\.?\d*)"

    for msg in messages:
        matches = re.findall(pattern, msg, re.IGNORECASE)
        for amt in matches:
            amt_clean = float(amt.replace(",", ""))
            amounts.append(amt_clean)
    
    return amounts
