def calculate_sensitivity(pii):

    score = 0

    if pii["Emails"]:
        score += 1

    if pii["Phone Numbers"]:
        score += 1

    if pii["PAN"]:
        score += 3

    if pii["Aadhaar"]:
        score += 3

    if score <= 1:
        level = "Low"

    elif score <= 3:
        level = "Medium"

    elif score <= 5:
        level = "High"

    else:
        level = "Critical"

    return {
        "Score": score,
        "Level": level
    }