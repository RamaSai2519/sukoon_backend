from shared.models.interfaces import CardGameInput as Input, Output
from shared.models.constants import OutputStatus
import string
import random


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def generate_random_alphabet_pairs(self, array_length):
        # Ensure the array length is even and within bounds
        if array_length % 2 != 0 or array_length > 52:
            raise ValueError(
                "Array length must be an even number and at most 52.")

        # Select the required number of unique letters
        alphabet = list(string.ascii_lowercase)[:array_length // 2]

        # Create pairs of each letter
        pairs = alphabet * 2

        # Shuffle the pairs to get random indices
        random.shuffle(pairs)

        return pairs

    def compute(self):
        number_of_cards_to_show = self.input.cards_to_show

        card_pairs_array = self.generate_random_alphabet_pairs(
            number_of_cards_to_show)

        return Output(
            output_details={"card_pairs_array": card_pairs_array},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )
