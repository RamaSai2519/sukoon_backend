from shared.helpers.base import call_graphql


def create_non_registered_user(mobile_number):

    query = """
        mutation MyMutation($mobileNumber: String!) {
            createUser(input: {status: NON_REGISTERED, mobileNumber: $mobileNumber}) {
                id
            }
        }
    """
    params = {"mobileNumber": mobile_number}
    return call_graphql(query=query, params=params, message="create_non_registered_user")


def update_user(user_data):

    query = """
        mutation MyMutation($input: UpdateUserInput) {
            updateUser(input: $input) {
                id
            }
        }
    """
    params = {"input": user_data}
    return call_graphql(query=query, params=params, message="update_user")
