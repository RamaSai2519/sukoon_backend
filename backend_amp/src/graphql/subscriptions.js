/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onCreateUser = /* GraphQL */ `
  subscription OnCreateUser($filter: ModelSubscriptionUserFilterInput) {
    onCreateUser(filter: $filter) {
      id
      firstName
      lastName
      gender
      isDeleted
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onUpdateUser = /* GraphQL */ `
  subscription OnUpdateUser($filter: ModelSubscriptionUserFilterInput) {
    onUpdateUser(filter: $filter) {
      id
      firstName
      lastName
      gender
      isDeleted
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onDeleteUser = /* GraphQL */ `
  subscription OnDeleteUser($filter: ModelSubscriptionUserFilterInput) {
    onDeleteUser(filter: $filter) {
      id
      firstName
      lastName
      gender
      isDeleted
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onCreateUserNotification = /* GraphQL */ `
  subscription OnCreateUserNotification(
    $filter: ModelSubscriptionUserNotificationFilterInput
  ) {
    onCreateUserNotification(filter: $filter) {
      id
      userId
      requestMeta
      externalMessageId
      status
      notificationType
      notificationJobType
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onUpdateUserNotification = /* GraphQL */ `
  subscription OnUpdateUserNotification(
    $filter: ModelSubscriptionUserNotificationFilterInput
  ) {
    onUpdateUserNotification(filter: $filter) {
      id
      userId
      requestMeta
      externalMessageId
      status
      notificationType
      notificationJobType
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onDeleteUserNotification = /* GraphQL */ `
  subscription OnDeleteUserNotification(
    $filter: ModelSubscriptionUserNotificationFilterInput
  ) {
    onDeleteUserNotification(filter: $filter) {
      id
      userId
      requestMeta
      externalMessageId
      status
      notificationType
      notificationJobType
      createdAt
      updatedAt
      __typename
    }
  }
`;
