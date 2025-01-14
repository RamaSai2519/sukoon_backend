from shared.models.interfaces import UpdateUserBalanceInput as Input, Output
from shared.db.users import get_user_balances_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.balances_collection = get_user_balances_collection()

    def compute(self) -> Output:
        query = {'user': self.input.user_id}
        balance = self.balances_collection.find_one(query)
        if self.input.action == 'plus':
            new_balance = balance[self.input.balance] + self.input.value
        elif self.input.action == 'minus':
            new_balance = balance[self.input.balance] - self.input.value

        self.balances_collection.update_one(
            query,
            {
                '$set': {
                    self.input.balance: new_balance
                }
            }
        )

        return Output(
            output_message="Successfully updated User Balance"
        )
