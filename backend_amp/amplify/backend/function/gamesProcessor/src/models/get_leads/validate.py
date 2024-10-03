from dataclasses import fields
from typing import get_origin, get_args, Optional, Union
from models.interfaces import GetLeadsInput as Input, User


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        user_fields = self.get_user_fields()
        filter_field, filter_value = self.input.filter_field, self.input.filter_value

        if not self.validate_filter_presence(filter_field, filter_value):
            return False, "Both filter_field and filter_value are required"

        if not self.validate_filter_field(filter_field, user_fields):
            return False, f"Invalid field {filter_field}"

        if not self.validate_filter_value_type(filter_field, filter_value, user_fields):
            return False, f"Invalid type for field {filter_field}: Expected {self.get_expected_type_str(filter_field, user_fields)}, got {type(filter_value).__name__}"

        return True, ""

    def get_user_fields(self) -> dict:
        return {f.name: f.type for f in fields(User)}

    def validate_filter_presence(self, filter_field, filter_value) -> bool:
        return not any([filter_field, filter_value]) or all([filter_field, filter_value])

    def validate_filter_field(self, filter_field, user_fields) -> bool:
        return not filter_field or filter_field in user_fields

    def validate_filter_value_type(self, filter_field, filter_value, user_fields) -> bool:
        expected_type = user_fields.get(filter_field, str)
        origin_type = get_origin(expected_type)

        if origin_type is Union:
            possible_types = get_args(expected_type)
            if filter_value is None and type(None) in possible_types:
                return True
            return any(isinstance(filter_value, typ) for typ in possible_types if typ is not type(None))
        else:
            return not filter_value or isinstance(filter_value, expected_type)

    def get_expected_type_str(self, filter_field, user_fields) -> str:
        expected_type = user_fields.get(filter_field, str)
        origin_type = get_origin(expected_type)

        if origin_type is Union:
            possible_types = get_args(expected_type)
            return ", ".join(t.__name__ for t in possible_types)
        else:
            return expected_type.__name__
