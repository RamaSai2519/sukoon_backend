from datetime import timedelta


class MainConfig:
    URL = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main"
    MARK_URL = "https://mark.sukoonunlimited.com"

    DB_CONFIG = {
        "connection_url": "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
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

    APPSYNC_API_KEY = "da2-jesqcxttxba57itwhh5m3neijm"
    AWS_DEFAULT_REGION = "ap-south-1"
    APPSYNC_ENDPOINT = "https://x3bch5zipbbwdlxc5efyhkas3y.appsync-api.ap-south-1.amazonaws.com/graphql"

    CASHFREE_API_CREDENTIALS = {
        "APP_ID": "7360545e44cee43e41b6f34584450637",
        "API_URL": "https://api.cashfree.com/pg/orders",
        "SECRET_KEY": "cfsk_ma_prod_cca5d658c985954f7d9047be10593a06_cfa55282"
    }

    EXPERT_JWT = "saltDemaze"
    JWT_SECRET_KEY = "AdminSecret-59737e2029b4aa10f3008f2a5cb372e537ba8d8a4bd05a87efb081d6634df175fec60167bf48cbfe399e5c98d7c8ea27137d44993ab28b71cfe2ae786f5d1952"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    AZURE_ENDPOINT = "https://sukoon-chat.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview"
    AZURE_KEY = "13c72289e9704b4ca63f683df19a7afe"
    AZURE_API_VERSION = "2023-03-15-preview"

    REGION = "ap-south-1"
    ACCESS_KEY = "AKIAXYKJVMCCK4G3OGPC"
    SECRET_ACCESS_KEY = "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"

    GRAPH_API_KEY = "da2-jesqcxttxba57itwhh5m3neijm"
    GRAPH_API_URL = "https://x3bch5zipbbwdlxc5efyhkas3y.appsync-api.ap-south-1.amazonaws.com/graphql"

    MAIN_BE_URL = "https://prod-backend.sukoonunlimited.com/api"

    SARATHI_SLACK_BOT_TOKEN = "xoxb-7127288803060-7529287532416-8SI5ACYFBDK9TjK1MPiw9xwU"
    USER_SLACK_BOT_TOKEN = "xoxb-7127288803060-7477543550820-23Gq4vGYi2F2UC7HSZL5Ayg2"

    FB_SERVER_KEY = "AAAAM5jkbNg:APA91bG80zQ8CzD1AeQmV45YT4yWuwSgJ5VwvyLrNynAJBk4AcyCb6vbCSGlIQeQFPAndS0TbXrgEL8HFYQq4DMXmSoJ4ek7nFcCwOEDq3Oi5Or_SibSpywYFrnolM4LSxpRkVeiYGDv"

    UNSPLASH_API_KEY = "I7e7Sy0qOspZ6whpNAp1gpCe4MXGIxWlMdSLBCfFpYI"

    GPT_VERSION = "2024-08-01-preview"
    GPT_API_KEY = "13c72289e9704b4ca63f683df19a7afe"
    GPT_ENDPOINT = "https://sukoon-chat.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

    ADA_VERSION = "2023-05-15"
    ADA_API_KEY = "13c72289e9704b4ca63f683df19a7afe"
    ADA_ENDPOINT = "https://sukoon-chat.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15"
