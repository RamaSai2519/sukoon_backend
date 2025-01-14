from shared.models.interfaces import UpdateUserBalanceInput as Input, Output
from shared.db.users import get_user_balances_collection
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.balances_collection = get_user_balances_collection()

    def compute(self) -> Output:
        query = {'user': ObjectId(self.input.user_id)}
        balance = self.balances_collection.find_one(query)
        if self.input.action == 'plus':
            new_balance = balance[self.input.balance] + self.input.value
        elif self.input.action == 'minus':
            new_balance = balance[self.input.balance] - self.input.value

        balance = self.balances_collection.find_one_and_update(
            query,
            {
                '$set': {
                    self.input.balance: new_balance
                }
            },
            return_document=True
        )

        return Output(
            output_message="Successfully updated User Balance"
        )
