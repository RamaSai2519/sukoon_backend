from datetime import timedelta


class DevConfig:
    DB_CONFIG = {
        "connection_url": "mongodb+srv://techcouncil:2lfNFMZIjdfZJl2R@cluster0.h3kssoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    }

    SMS_API_CONFIG = {
        "userid": "2000241133",
        "password": "Tech@sukoon98",
        "method": "SendMessage",
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

    EXPERT_JWT = "saltDemaze"
    JWT_SECRET_KEY = "AdminSecret-59737e2029b4aa10f3008f2a5cb372e537ba8d8a4bd05a87efb081d6634df175fec60167bf48cbfe399e5c98d7c8ea27137d44993ab28b71cfe2ae786f5d1952"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    AZURE_ENDPOINT = "https://sukoon-chat.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview"
    AZURE_KEY = "13c72289e9704b4ca63f683df19a7afe"
    AZURE_API_VERSION = "2023-03-15-preview"

    REGION = "ap-south-1"
    ACCESS_KEY = "AKIAXYKJVMCCBZESPREV"
    SECRET_ACCESS_KEY = "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"

    GRAPH_API_KEY = "da2-jesqcxttxba57itwhh5m3neijm"
    GRAPH_API_URL = "https://x3bch5zipbbwdlxc5efyhkas3y.appsync-api.ap-south-1.amazonaws.com/graphql"

    MAIN_BE_URL = "https://prod-backend.sukoonunlimited.com/api"

    SLACK_BOT_TOKEN = "xoxb-7127288803060-7529287532416-8SI5ACYFBDK9TjK1MPiw9xwU"

    FB_SERVER_KEY = "AAAAM5jkbNg:APA91bG80zQ8CzD1AeQmV45YT4yWuwSgJ5VwvyLrNynAJBk4AcyCb6vbCSGlIQeQFPAndS0TbXrgEL8HFYQq4DMXmSoJ4ek7nFcCwOEDq3Oi5Or_SibSpywYFrnolM4LSxpRkVeiYGDv"

    UNSPLASH_API_KEY = "I7e7Sy0qOspZ6whpNAp1gpCe4MXGIxWlMdSLBCfFpYI"
