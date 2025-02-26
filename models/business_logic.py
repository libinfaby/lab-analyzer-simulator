import random

class BusinessLogic:
    @staticmethod
    def generate_result(lower_range, upper_range):
        return round(random.uniform(lower_range, upper_range), 3)