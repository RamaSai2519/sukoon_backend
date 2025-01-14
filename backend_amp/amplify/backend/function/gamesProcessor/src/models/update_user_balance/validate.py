from shared.db.users import get_user_collection, get_user_balances_collection
from shared.models.interfaces import UpdateUserBalanceInput as Input, UserBalance


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.balances_collection = get_user_balances_collection()

    def validate_input(self) -> tuple:
        query = {'_id': self.input.user_id}
        user = self.users_collection.find_one(query)
        if not user:
            return False, "User not found"

        query = {'user': self.input.user_id}
        balance = self.balances_collection.find_one(query)
        if not balance:
            return False, "Balance not found"

        if self.input.balance not in UserBalance.__dataclass_fields__.keys():
            return False, "Invalid balance field"

        if not isinstance(self.input.value, int):
            return False, "Invalid value"

        if self.input.action not in ['plus', 'minus']:
            return False, "Invalid action"

        return True, ""
