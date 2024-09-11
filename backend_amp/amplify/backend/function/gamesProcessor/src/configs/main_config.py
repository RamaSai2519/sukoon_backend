from datetime import timedelta


class MainConfig:
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

    JWT_SECRET_KEY = "AdminSecret-59737e2029b4aa10f3008f2a5cb372e537ba8d8a4bd05a87efb081d6634df175fec60167bf48cbfe399e5c98d7c8ea27137d44993ab28b71cfe2ae786f5d1952"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    EXPERT_JWT = "saltDemaze"

    REGION = "ap-south-1"
    ACCESS_KEY = "AKIAXYKJVMCCBZESPREV"
    SECRET_ACCESS_KEY = "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"

    GRAPH_API_KEY = "da2-jesqcxttxba57itwhh5m3neijm"
    GRAPH_API_URL = "https://x3bch5zipbbwdlxc5efyhkas3y.appsync-api.ap-south-1.amazonaws.com/graphql"
    
    MAIN_BE_URL = "https://prod-backend.sukoonunlimited.com/api"
    
    SLACK_BOT_TOKEN = "xoxb-7127288803060-7529287532416-8SI5ACYFBDK9TjK1MPiw9xwU"
    
    FB_SERVER_KEY = "AAAAM5jkbNg:APA91bG80zQ8CzD1AeQmV45YT4yWuwSgJ5VwvyLrNynAJBk4AcyCb6vbCSGlIQeQFPAndS0TbXrgEL8HFYQq4DMXmSoJ4ek7nFcCwOEDq3Oi5Or_SibSpywYFrnolM4LSxpRkVeiYGDv"
