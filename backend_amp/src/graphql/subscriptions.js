/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onCreateTodo = /* GraphQL */ `
  subscription OnCreateTodo($filter: ModelSubscriptionTodoFilterInput) {
    onCreateTodo(filter: $filter) {
      id
      name
      description
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onUpdateTodo = /* GraphQL */ `
  subscription OnUpdateTodo($filter: ModelSubscriptionTodoFilterInput) {
    onUpdateTodo(filter: $filter) {
      id
      name
      description
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onDeleteTodo = /* GraphQL */ `
  subscription OnDeleteTodo($filter: ModelSubscriptionTodoFilterInput) {
    onDeleteTodo(filter: $filter) {
      id
      name
      description
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
      name
      description
      notificationType
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
      name
      description
      notificationType
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
      name
      description
      notificationType
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onCreateUserGame = /* GraphQL */ `
  subscription OnCreateUserGame($filter: ModelSubscriptionUserGameFilterInput) {
    onCreateUserGame(filter: $filter) {
      id
      name
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onUpdateUserGame = /* GraphQL */ `
  subscription OnUpdateUserGame($filter: ModelSubscriptionUserGameFilterInput) {
    onUpdateUserGame(filter: $filter) {
      id
      name
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onDeleteUserGame = /* GraphQL */ `
  subscription OnDeleteUserGame($filter: ModelSubscriptionUserGameFilterInput) {
    onDeleteUserGame(filter: $filter) {
      id
      name
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onCreateUserPlay = /* GraphQL */ `
  subscription OnCreateUserPlay($filter: ModelSubscriptionUserPlayFilterInput) {
    onCreateUserPlay(filter: $filter) {
      id
      play
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onUpdateUserPlay = /* GraphQL */ `
  subscription OnUpdateUserPlay($filter: ModelSubscriptionUserPlayFilterInput) {
    onUpdateUserPlay(filter: $filter) {
      id
      play
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const onDeleteUserPlay = /* GraphQL */ `
  subscription OnDeleteUserPlay($filter: ModelSubscriptionUserPlayFilterInput) {
    onDeleteUserPlay(filter: $filter) {
      id
      play
      createdAt
      updatedAt
      __typename
    }
  }
`;
