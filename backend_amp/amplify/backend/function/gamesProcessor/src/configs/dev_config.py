from datetime import timedelta


class DevConfig:
    DB_CONFIG = {
        "connection_url": "mongodb+srv://techcouncil:2lfNFMZIjdfZJl2R@cluster0.h3kssoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    }

    SMS_API_CONFIG = {
        "userid": "2000241133",
        "password": "Tech@sukoon98",
        "method": "SendMessage",
        "msg": "Dear user, use __otp__ as One Time Password generated by Three Dots & Dash to log in to your Sukoon.Love account.",
        "msg_type": "TEXT",
        "auth_scheme": "plain",
        "v": "1.1",
        "format": "text"
    }

    SMS_API_URL = "http://enterprise.smsgupshup.com/GatewayAPI/rest"

    WHATSAPP_API = {
        "URL": "https://graph.facebook.com/v19.0/332782693255519/messages",
        "ACCESS_TOKEN": "EAAQFy4A7ZCfABO1UJeKTvjzWFEyqnuP42JZCBZBe7XruAD5SIQEc0ukrOB0HunFgiG0kyBaoPcnX9PLPjewwSCNOYxOZCwW2GqZBsUjZAFEtZCLKwJn9asnntcX9bWd7SbhrAzzhyVsPxbCubQJLqZC5lBGgp9TzpOUO5T12ZBRmSn1MR9BtMNVVvIS2wc2lchvt1"
    }

    PUSH_NOTIFICATION_API = {
        "URL": "https://fcm.googleapis.com/v1/projects/sukoonlove-007/messages:send",
        "ACCESS_TOKEN": "AIzaSyAMJotLhCHDZQav-pI3xwh94zK9f2A62r8"
    }

    APPSYNC_API_KEY = "da2-vkps47zevzerdkqvgklaxjryua"
    AWS_DEFAULT_REGION = "ap-south-1"
    APPSYNC_ENDPOINT = "https://gxuleyn72fhzbjnvylyr73f7gu.appsync-api.ap-south-1.amazonaws.com/graphql"

    CASHFREE_API_CREDENTIALS = {
        "API_URL": "https://sandbox.cashfree.com/pg/orders",
        "APP_ID": "TEST102789038ae976e3fbbc30921f6f30987201",
        "SECRET_KEY": "cfsk_ma_test_c05c620df7e15efa2a1aa28db78b812b_581b676c"
    }

    JWT_SECRET_KEY = "AdminSecret-59737e2029b4aa10f3008f2a5cb372e537ba8d8a4bd05a87efb081d6634df175fec60167bf48cbfe399e5c98d7c8ea27137d44993ab28b71cfe2ae786f5d1952"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
