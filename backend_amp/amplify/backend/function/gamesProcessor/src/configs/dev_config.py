class DevConfig:
    DB_CONFIG = {
        "connection_url" : "mongodb+srv://techcouncil:2lfNFMZIjdfZJl2R@cluster0.h3kssoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    }
    SMS_API_CONFIG = {
        "userid": "2000241133",
        "password": "FJGtU6wH",
        "method": "SendMessage",
        "msg": "Dear user, use __otp__ as One Time Password generated by Three Dots & Dash to log in to your Sukoon.Love account.",
        "msg_type": "TEXT",
        "auth_scheme": "plain",
        "v": "1.1",
        "format": "text"
    }
    SMS_API_URL = "https://enterprise.smsgupshup.com/GatewayAPI/rest"


    WHATSAPP_API = {
        "URL": "https://graph.facebook.com/v19.0/332782693255519/messages",
        "ACCESS_TOKEN": "EAAQFy4A7ZCfABO1UJeKTvjzWFEyqnuP42JZCBZBe7XruAD5SIQEc0ukrOB0HunFgiG0kyBaoPcnX9PLPjewwSCNOYxOZCwW2GqZBsUjZAFEtZCLKwJn9asnntcX9bWd7SbhrAzzhyVsPxbCubQJLqZC5lBGgp9TzpOUO5T12ZBRmSn1MR9BtMNVVvIS2wc2lchvt1"
    }

    
