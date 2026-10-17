import math


def calculate_required_quantity(need, people_affected):
    """Calculate illustrative resource quantities for FloodSense."""

    if people_affected is None or people_affected <= 0:
        raise ValueError("People affected must be greater than zero.")

    category = need.strip().lower()

    if category == "food":
        # Demo assumption: 3 food packets per person
        return people_affected * 3

    elif category == "rescue":
        # Demo assumption: 1 boat per 10 people
        return math.ceil(people_affected / 10)

    elif category == "medical":
        # Demo assumption: 1 First Aid Kit per 10 people
        return math.ceil(people_affected / 10)

    elif category == "water":
        # Demo assumption: 3 litres per person
        return people_affected * 3

    elif category == "shelter":
        # Demo assumption: 1 blanket per 5 people
        return math.ceil(people_affected / 5)

    else:
        raise ValueError(
            f"Quantity calculation not defined for {need}."
        )