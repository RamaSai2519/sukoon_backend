from shared.models.interfaces import UpsertOfferInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_flat_discount(self) -> tuple:
        try:
            int(self.input.flatDiscount)
        except ValueError:
            return False, 'flatDiscount should be an integer'

        if int(self.input.flatDiscount) < 0:
            return False, 'flatDiscount should be a positive integer'

        return True, ''

    def validate_percentage_discount(self) -> tuple:
        try:
            float(self.input.discountPercentage)
        except ValueError:
            return False, 'discountPercentage should be a float'

        if float(self.input.discountPercentage) < 0:
            return False, 'discountPercentage should be a positive float'

        return True, ''

    def validate_code_offer(self) -> tuple:
        if not self.input.flatDiscount and not self.input.discountPercentage:
            return False, 'Either flatDiscount or percentageDiscount is required'

        if self.input.flatDiscount and self.input.discountPercentage:
            return False, 'Only one of flatDiscount or percentageDiscount is allowed'

        if self.input.flatDiscount:
            return self.validate_flat_discount()

        if self.input.discountPercentage:
            return self.validate_percentage_discount()

        return True, ''

    def validate_input(self) -> tuple:
        if self.input.offer_type not in ['code', 'partner']:
            return False, 'offer_type should be either "code" or "partner"'

        if self.input.offer_type == 'partner':
            if not self.input.website:
                return False, 'website is required for partner offers'
            if self.input.flatDiscount or self.input.discountPercentage:
                return False, 'flatDiscount and discountPercentage are not allowed for partner offers'

        if self.input.offer_type == 'code':
            return self.validate_code_offer()

        return True, ''
