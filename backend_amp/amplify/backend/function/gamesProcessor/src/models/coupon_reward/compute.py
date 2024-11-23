from bson import ObjectId
from shared.models.interfaces import CouponRewardInput as Input, Output
from shared.models.constants import OutputStatus
from shared.db.users import get_user_collection
import random


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def _get_reward_amount(self) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(self.input.user_id)})

        first_three_games_gift_probabilities = {
            10: 0.40,
            20: 0.30,
            25: 0.20,
            50: 0.05,
            75: 0.03,
            100: 0.02
        }
        gift_probabilities = {
            10: 0.40,
            20: 0.30,
            25: 0.20,
            50: 0.05,
            75: 0.03,
            100: 0.02
        }

        random_number = random.random()
        print(random_number)

        cumulative_probability = 0

        for gift, probability in gift_probabilities.items():
            cumulative_probability += probability

            if random_number < cumulative_probability:
                return gift

        # If no gift is returned, return the last gift
        return list(gift_probabilities.keys())[-1]

    def compute(self):

        reward_amount = self._get_reward_amount()

        return Output(
            output_details={"reward_amount": reward_amount},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched reward amount"
        )
