from helpers.base import call_graphql

def fetch_user_by_mobile_number(mobile_number):

    query = """
        query MyQuery($mobileNumber: String!) {
            userByMobileNumber(mobileNumber: $mobileNumber) {
                items {
                    id
                    firstName
                    gender
                    dateOfBirth
                    lastName
                    interestedInClubSukoon
                    mobileNumber
                }
            }
        }
    """
    params = {"mobileNumber": mobile_number}
    return call_graphql(query=query , params=params, message="fetch_user_by_mobile_number").get("userByMobileNumber")
