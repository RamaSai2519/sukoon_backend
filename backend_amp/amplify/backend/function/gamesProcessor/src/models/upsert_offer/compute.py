from datetime import datetime
from shared.models.common import Common
from shared.db.referral import get_offers_collection
from shared.models.constants import OutputStatus, ConstantStrings
from shared.models.interfaces import UpsertOfferInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.offers_collection = get_offers_collection()
        self.COUPON_CODE = ConstantStrings.COUPON_CODE
        self.FLAT_DISCOUNT = ConstantStrings.FLAT_DISCOUNT
        self.DISCOUNT_PERCENTAGE = ConstantStrings.DISCOUNT_PERCENTAGE

    def pop_immutable_fields(self, new_data: dict) -> dict:
        fields = ["_id"]
        for field in fields:
            new_data.pop(field, None)
        return new_data

    def merge_old_data(self, new_data: dict, old_data: dict) -> dict:
        for key, value in old_data.items():
            if key not in new_data or new_data[key] is None or new_data[key] == "" or new_data[key] == []:
                new_data[key] = value

        if self.DISCOUNT_PERCENTAGE in new_data:
            new_data.pop(self.FLAT_DISCOUNT, None)
        elif self.FLAT_DISCOUNT in new_data:
            new_data.pop(self.DISCOUNT_PERCENTAGE, None)

        return new_data

    def set_defaults(self, new_data: dict) -> dict:
        new_data["createdDate"] = datetime.now()
        return new_data

    def calculate_final_price(self, new_data: dict) -> dict:
        if self.DISCOUNT_PERCENTAGE in new_data:
            new_data["finalPrice"] = new_data["actual_price"] - \
                (new_data["actual_price"] *
                 new_data[self.DISCOUNT_PERCENTAGE] / 100)
        elif self.FLAT_DISCOUNT in new_data:
            new_data["finalPrice"] = new_data["actual_price"] - \
                new_data[self.FLAT_DISCOUNT]
        return new_data

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        new_data = {k: v for k, v in new_data.items() if v is not None}
        if old_data:
            new_data = self.pop_immutable_fields(new_data)
            new_data = self.merge_old_data(new_data, old_data)
        else:
            new_data = self.set_defaults(new_data)

        if isinstance(new_data["validTill"], str):
            new_data["validTill"] = Common.string_to_date(
                new_data, "validTill")

        float_fields = [self.DISCOUNT_PERCENTAGE, self.FLAT_DISCOUNT]
        for field in float_fields:
            if field in new_data:
                new_data[field] = float(new_data[field])

        new_data[self.COUPON_CODE] = str(new_data[self.COUPON_CODE]).upper()
        new_data = self.calculate_final_price(new_data)

        return new_data

    def get_old_data(self) -> dict:
        query = {self.COUPON_CODE: self.input.couponCode}
        old_data = self.offers_collection.find_one(query)
        if not old_data:
            return None
        old_data = Common.clean_dict(old_data, Input)
        return old_data

    def compute(self) -> Output:
        new_data = self.input.__dict__
        old_data = self.get_old_data()

        message = "Offer Upsert failed"
        if old_data:
            new_data = self.prep_data(new_data, old_data)
            self.offers_collection.update_one(
                {self.COUPON_CODE: old_data.get(self.COUPON_CODE)}, {"$set": new_data})
            message = "Offer updated successfully"
        else:
            new_data = self.prep_data(new_data)
            self.offers_collection.insert_one(new_data)
            message = "Offer created successfully"

        return Output(
            output_details=Common.jsonify(new_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
