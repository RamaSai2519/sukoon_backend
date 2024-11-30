from shared.models.interfaces import UpsertOfferInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_flat_discount(self):
        try:
            int(self.input.flatDiscount)
        except ValueError:
            return False, "flatDiscount should be an integer"

        if int(self.input.flatDiscount) < 0:
            return False, "flatDiscount should be a positive integer"

        return True, ""

    def validate_percentage_discount(self):
        try:
            float(self.input.discountPercentage)
        except ValueError:
            return False, "discountPercentage should be a float"

        if float(self.input.discountPercentage) < 0:
            return False, "discountPercentage should be a positive float"

        return True, ""

    def validate_input(self):
        if not self.input.flatDiscount and not self.input.discountPercentage:
            return False, "Either flatDiscount or percentageDiscount is required"

        if self.input.flatDiscount and self.input.discountPercentage:
            return False, "Only one of flatDiscount or percentageDiscount is allowed"

        if self.input.flatDiscount:
            return self.validate_flat_discount()

        if self.input.discountPercentage:
            return self.validate_percentage_discount()

        return True, ""
