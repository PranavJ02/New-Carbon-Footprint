def calculate_transport(distance):
    return distance * 0.21


def calculate_electricity(units):
    return units * 0.5


def calculate_food(meals):
    return meals * 2.5


def total_emission(t, e, f):
    return t + e + f