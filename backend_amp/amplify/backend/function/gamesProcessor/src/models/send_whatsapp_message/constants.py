class WhatsappNotificationTemplates:
    def __init__(self) -> None:
        self.REMINDER_FOR_WEBINAR = {
            "template_name": "Reminder for Webinar",
            "template": {
                "name": "reminder_for_webinar",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{sarathi_name}"},
                            {"type": "text", "text": "{guest_speaker_name}"},
                            {"type": "text", "text": "{date}"},
                            {"type": "text", "text": "{time}"},
                            {"type": "text", "text": "{event_name}"},
                        ],
                    },
                    {
                        "type": "button",
                        "index": "0",
                        "sub_type": "flow",
                    },
                ],
            },
        }

        self.GAMES_GALA_1 = {
            "template_name": "Games Gala",
            "template": {
                "name": "games_gala_marketing_message",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                        ],
                    },
                ],
            },
        }

        self.GAMES_GALA_2 = {
            "template_name": "Games Gala",
            "template": {
                "name": "games_gala",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "video", "video": {"link": "{video_link}"}}
                        ],
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                        ],
                    },
                ],
            },
        }


        self.NON_REGISTERED_USER_QUERY = {
            "template_name": "Non Registered User Query",
            "template": {
                "name": "non_registered_user_query",
                "language": {"code": "en"},
            },
        }

        self.REGISTERED_USER_QUERY = {
            "template_name": "Registered User Query",
            "template": {
                "name": "registered_user_query",
                "language": {"code": "en"},
            },
        }

        self.REGISTERED_USER_ONLY_EVENT_ACTIVE = {
            "template_name": "Registered User Only Event Active",
            "template": {
                "name": "registered_user_only_event_active",
                "language": {"code": "en"},
            },
        }


        self.COMMON_CALL_REPLY = {
            "template_name": "Common Call Reply",
            "template": {
                "name": "common_call_reply",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{mobile_number}"},
                        ],
                    },
                ],
            },
        }

        self.FIX_TIME_REPLY = {
            "template_name": "Fix Time Reply",
            "template": {
                "name": "fix_time_reply",
                "language": {"code": "en"},
            },
        }


        self.GAMES_EVENT = {
            "template_name": "Games Event",
            "template": {
                "name": "games_event",
                "language": {"code": "en"},
            },
        }


        self.GAMES_MARKETING_MESSAGE = {
            "template_name": "Games Marketing Message",
            "template": {
                "name": "games_marketing_message",
                "language": {"code": "en"},
            },
        }

        self.GAMES_WINNER = {
            "template_name": "Games Marketing Message",
            "template": {
                "name": "games_winner",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{amazon_link}"},
                        ],
                    },

                ],
            },
        }

        self.WELCOME_REGISTRATION = {
            "template_name": "Welcome Registration",
            "template": {
                "name": "welcome_registration",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                        ],
                    },

                ],
            },
        }

        self.HOLISTIC_WELLNESS = {
            "template_name": "Holistic Wellness",
            "template": {
                "name": "holistic_wellness",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                ],
            },
        }

        self.FEEDBACK_SURVEY = {
            "template_name": "Feedback survey",
            "template": {
                "name": "feedback_survey",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{sarathi_name}"},
                        ],
                    },
                    {
                        "type": "button",
                        "index": "0",
                        "sub_type": "flow",
                    },
                ],
            },
        }

        self.WEEKEND_TEMPLATE = {
            "template_name": "Weekend Template",
            "template": {
                "name": "weekend_message_template",
                "language": {"code": "en"},
            },
        }

        self.SANDHYA_TEMPLATE = {
            "template_name": "Sandhya Template",
            "template": {
                "name": "sandhya_template",
                "language": {"code": "en"},
            },
        }


        self.DEMENTIA = {
            "template_name": "DEMENTIA",
            "template": {
                "name": "dementia_template",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                ],
            },
        }

        self.EVENT_REGISTRATION = {
            "template_name": "Event Registration",
            "template": {
                "name": "event_registration",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{custom_text}"},
                            {"type": "text", "text": "{topic_name}"},
                            {"type": "text", "text": "{speakers_name}"},
                            {"type": "text", "text": "{date_and_time}"},
                            {"type": "text", "text": "{where}"},
                            {"type": "text", "text": "{registration_link}"},
                            {"type": "text", "text": "{phone_number}"},
                            {"type": "text", "text": "{whatsapp_community_link}"},
                        ],
                    },
                    {
                        "type": "button",
                        "index": "0",
                        "sub_type": "url",
                        "parameters": [{"type": "text", "text": "{registraion_link_slug}"}],
                    },
                ],
            },
        }

        self.EVENT_REGISTRATION_CONFIRMATION = {
            "template_name": "Event Registration Confirmation",
            "template": {
                "name": "event_registration_confirmation",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{custom_text}"},
                            {"type": "text", "text": "{topic_name}"},
                            {"type": "text", "text": "{speakers_name}"},
                            {"type": "text", "text": "{date_and_time}"},
                            {"type": "text", "text": "{where}"},
                            {"type": "text", "text": "{phone_number}"},
                            {"type": "text", "text": "{whatsapp_community_link}"},
                        ],
                    },
                ],
            },
        }

        self.EVENT_REMINDER = {
            "template_name": "Event Reminder",
            "template": {
                "name": "event_reminder",
                "language": {"code": "en"},
                "components": [
                   {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                            {"type": "text", "text": "{topic_name}"},
                            {"type": "text", "text": "{date_and_time}"},
                            {"type": "text", "text": "{where}"},
                            {"type": "text", "text": "{phone_number}"},
                            {"type": "text", "text": "{whatsapp_community_link}"},
                        ],
                    },
                ],
            },
        }

        self.STEP_UP_CHALLENGE = {
            "template_name": "STEP_UP_CHALLENGE",
            "template": {
                "name": "step_up_challenge",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                ],
            },
        }

        self.MARKET_REMINDER_MESSAGE = {
            "template_name": "MARKET_REMINDER_MESSAGE",
            "template": {
                "name": "market_reminder_message",
                "language": {"code": "en"},
            },
        }


        self.AGING_MESSAGE = {
            "template_name": "AGING_MESSAGE",
            "template": {
                "name": "aging_template",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                ],
            },
        }

        self.GAMES_TEMPLATE = {
            "template_name": "GAMES_TEMPLATE",
            "template": {
                "name": "games_template",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{sarathi_name}"},
                            {"type": "text", "text": "{game_link}"},
                        ],
                    },
                ],
            },
        }

        self.CHARGE_LIFE_TEMPLATE = {
            "template_name": "CHARGE_LIFE_TEMPLATE",
            "template": {
                "name": "charge_life_template",
                "language": {"code": "en"},
            },
        }

        self.CLUB_SUKOON_MEMBERSHIP = {
            "template_name": "CLUB_SUKOON_MEMBERSHIP",
            "template": {
                "name": "club_sukoon_membership",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                        ],
                    },

                ],
            },
        }

        self.PARTIAL_LEADS = {
            "template_name": "PARTIAL_LEADS",
            "template": {
                "name": "partial_leads",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "{user_name}"},
                        ],
                    },

                ],
            },
        }


        self.NEST_SUPPORT = {
            "template_name": "NEST_SUPPORT",
            "template": {
                "name": "nest_support",
                "language": {"code": "en"},
                "components": [
                    {       
                        "type": "header",
                        "parameters": [
                            {"type": "image", "image": {"link": "{image_link}"}}
                        ],
                    },
                ],
            },
        }
