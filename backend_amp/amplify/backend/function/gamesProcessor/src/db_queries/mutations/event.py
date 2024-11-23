from shared.helpers.base import call_graphql


def update_event(event_data):

    query = """
        mutation MyMutation($input: UpdateEventInput!) {
            updateEvent(input: $input) {
                id
            }
        }
    """
    params = {"input": event_data}
    return call_graphql(query=query, params=params, message="update_event")


def create_event(event_data):

    query = """
        mutation MyMutation2($input: CreateEventInput!) {
            createEvent(input: $input) {
                id
            }
        }
    """
    params = {"input": event_data}
    return call_graphql(query=query, params=params, message="create_event")
