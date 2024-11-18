import bcrypt
from models.common import Common
from models.constants import OutputStatus
from db.users import get_admins_collection
from flask_jwt_extended import jwt_required
from models.interfaces import AdminAuthInput as Input, Admin, Output
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.admins_collection = get_admins_collection()

    def validate_phoneNumber(self) -> bool:
        if self.admins_collection.find_one({"phoneNumber": self.input.phoneNumber}):
            return True
        return False

    def sign_up(self) -> Output:
        if self.validate_phoneNumber():
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Phone number already exists"
            )

        hashed_password = bcrypt.hashpw(
            self.input.password.encode("utf-8"), bcrypt.gensalt())

        admin_data = Admin(
            name=self.input.name,
            phoneNumber=self.input.phoneNumber,
            password=hashed_password.decode("utf-8"),
        )
        admin_doc = admin_data.__dict__
        del admin_doc["_id"]

        admin_id = self.admins_collection.insert_one(admin_doc).inserted_id
        admin_data._id = admin_id

        return Output(
            output_details=Common.jsonify(admin_data.__dict__),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully registered"
        )

    def sign_in(self) -> Output:
        admin_data = Admin(
            **dict(self.admins_collection.find_one({"phoneNumber": self.input.phoneNumber}))
        )

        if not admin_data or not bcrypt.checkpw(self.input.password.encode("utf-8"), admin_data.password.encode("utf-8")):
            return Output(
                output_details=self.input.__dict__,
                output_status=OutputStatus.FAILURE,
                output_message="Bad Credentials"
            )

        admin_id = str(admin_data._id)
        access_token = create_access_token(identity=admin_id)
        refresh_token = create_refresh_token(identity=admin_id)

        output_details = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": Common.jsonify(admin_data.__dict__)
        }

        return Output(
            output_details=output_details,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully signed in"
        )

    @jwt_required(refresh=True)
    def refresh_token(self) -> Output:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return Output(
            output_details={"access_token": access_token},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully refreshed token"
        )

    def compute(self) -> Output:
        if self.input.action == "register":
            return self.sign_up()
        elif self.input.action == "login":
            return self.sign_in()
        elif self.input.action == "refresh":
            return self.refresh_token()
        else:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Invalid action"
            )
