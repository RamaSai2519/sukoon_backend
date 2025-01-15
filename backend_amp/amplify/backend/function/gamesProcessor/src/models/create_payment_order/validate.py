from shared.models.interfaces import CreatePaymentOrderInput as Input
from shared.db.users import get_subscription_plans_collection
from shared.models.constants import pay_types


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.plans_collection = get_subscription_plans_collection()

    def validate_input(self):
        types = [pay_type["type"] for pay_type in pay_types]
        if self.input.pay_type and self.input.pay_type not in types:
            return False, "Invalid payment type"

        # query = {'name': self.input.plan}
        # plan = self.plans_collection.find_one(query)
        # if not plan:
        #     return False, "Invalid plan"

        return True, ""
