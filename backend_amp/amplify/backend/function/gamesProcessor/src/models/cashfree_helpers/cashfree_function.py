from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
import os
from cashfree_pg.models.customer_details import CustomerDetails
from configs import CONFIG as CONFIG

ENV = os.environ.get("ENV")
CASHFREE_CREDENTIALS = CONFIG.CASHFREE_API_CREDENTIALS

Cashfree.XClientId = CASHFREE_CREDENTIALS.get("APP_ID")
Cashfree.XClientSecret = CASHFREE_CREDENTIALS.get("SECRET_KEY")

Cashfree.XEnvironment = Cashfree.XProduction if ENV == "main" else Cashfree.XSandbox
x_api_version = "2023-08-01"

def get_cashfree_payment_session_id(customer_details_dict, order_details_dict):

    phone_number = customer_details_dict.get("phone_number")
    customer_id = customer_details_dict.get("customer_id")
    customer_name = customer_details_dict.get("customer_name")
    order_id = order_details_dict.get("order_id")
    order_amount = order_details_dict.get("order_amount")

    customerDetails = CustomerDetails(customer_phone=phone_number, customer_name= customer_name, customer_id = customer_id)
    createOrderRequest = CreateOrderRequest(order_id= order_id ,order_amount=order_amount, order_currency="INR", customer_details=customerDetails)

    try:
        print(Cashfree.XClientId , Cashfree.XClientSecret, Cashfree.XEnvironment)
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        print(api_response.data, "vfvvfdshjbbhjdsvvbhjsdvhbjhbjcshbjhjc")
        return api_response
    
    except Exception as e:
        print(f"Some Error occured while creating payment order using Cashfree. The error which occured is {e}")
        return None