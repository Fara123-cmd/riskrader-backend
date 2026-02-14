# backend/crowd_density.py

def crowd_density(hour, area_type):
    """
    Estimate crowd density based on time (0–23) and area type
    Returns: Low / Medium / High
    """

    if hour is None:
        return "Medium"

    try:
        hour = int(hour)
    except:
        return "Medium"

    area_type = area_type.lower() if area_type else "unknown"

    # Residential areas
    if area_type == "residential":
        if 6 <= hour <= 9 or 18 <= hour <= 21:
            return "Medium"
        elif 22 <= hour or hour <= 5:
            return "Low"
        else:
            return "Medium"

    # Commercial areas
    if area_type == "commercial":
        if 9 <= hour <= 21:
            return "High"
        else:
            return "Low"

    # Public / unknown areas
    if 7 <= hour <= 20:
        return "Medium"

    return "Low"


def crowd_alert(level):
    """
    Generate user-friendly alert based on crowd density
    """

    if level == "Low":
        return "⚠️ Low crowd presence. Avoid staying alone. Prefer crowded areas."
    elif level == "Medium":
        return "ℹ️ Moderate crowd presence. Stay alert and aware."
    else:
        return "✅ High crowd presence. Area is relatively safer."
