from helpers.base import call_graphql


def update_user_notification_message_id(notification_id, message_id):
    query = """

        mutation MyMutation3($id: ID!, $externalMessageId: String) {
            updateUserNotification(input: {id: $id, externalMessageId: $externalMessageId}) {
                id
            }
        }
"""
    params = {"id": notification_id, "externalMessageId": message_id}
    return call_graphql(query=query , params=params, message="update_user_notification_message_id")