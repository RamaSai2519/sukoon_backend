/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createUser = /* GraphQL */ `
  mutation CreateUser(
    $input: CreateUserInput!
    $condition: ModelUserConditionInput
  ) {
    createUser(input: $input, condition: $condition) {
      id
      firstName
      lastName
      gender
      status
      isDeleted
      interestedInClubSukoon
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      userConversationsAsUser {
        nextToken
        __typename
      }
      userConversationsAsSarathi {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateUser = /* GraphQL */ `
  mutation UpdateUser(
    $input: UpdateUserInput!
    $condition: ModelUserConditionInput
  ) {
    updateUser(input: $input, condition: $condition) {
      id
      firstName
      lastName
      gender
      status
      isDeleted
      interestedInClubSukoon
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      userConversationsAsUser {
        nextToken
        __typename
      }
      userConversationsAsSarathi {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteUser = /* GraphQL */ `
  mutation DeleteUser(
    $input: DeleteUserInput!
    $condition: ModelUserConditionInput
  ) {
    deleteUser(input: $input, condition: $condition) {
      id
      firstName
      lastName
      gender
      status
      isDeleted
      interestedInClubSukoon
      dateOfBirth
      mobileNumber
      userNotifications {
        nextToken
        __typename
      }
      userConversationsAsUser {
        nextToken
        __typename
      }
      userConversationsAsSarathi {
        nextToken
        __typename
      }
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createUserNotification = /* GraphQL */ `
  mutation CreateUserNotification(
    $input: CreateUserNotificationInput!
    $condition: ModelUserNotificationConditionInput
  ) {
    createUserNotification(input: $input, condition: $condition) {
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
export const updateUserNotification = /* GraphQL */ `
  mutation UpdateUserNotification(
    $input: UpdateUserNotificationInput!
    $condition: ModelUserNotificationConditionInput
  ) {
    updateUserNotification(input: $input, condition: $condition) {
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
export const deleteUserNotification = /* GraphQL */ `
  mutation DeleteUserNotification(
    $input: DeleteUserNotificationInput!
    $condition: ModelUserNotificationConditionInput
  ) {
    deleteUserNotification(input: $input, condition: $condition) {
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
export const createScheduledJobs = /* GraphQL */ `
  mutation CreateScheduledJobs(
    $input: CreateScheduledJobsInput!
    $condition: ModelScheduledJobsConditionInput
  ) {
    createScheduledJobs(input: $input, condition: $condition) {
      id
      scheduledJobType
      scheduledJobTime
      user_requested
      status
      isDeleted
      scheduledJobStatus
      requestMeta
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateScheduledJobs = /* GraphQL */ `
  mutation UpdateScheduledJobs(
    $input: UpdateScheduledJobsInput!
    $condition: ModelScheduledJobsConditionInput
  ) {
    updateScheduledJobs(input: $input, condition: $condition) {
      id
      scheduledJobType
      scheduledJobTime
      user_requested
      status
      isDeleted
      scheduledJobStatus
      requestMeta
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteScheduledJobs = /* GraphQL */ `
  mutation DeleteScheduledJobs(
    $input: DeleteScheduledJobsInput!
    $condition: ModelScheduledJobsConditionInput
  ) {
    deleteScheduledJobs(input: $input, condition: $condition) {
      id
      scheduledJobType
      scheduledJobTime
      user_requested
      status
      isDeleted
      scheduledJobStatus
      requestMeta
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createUserConversations = /* GraphQL */ `
  mutation CreateUserConversations(
    $input: CreateUserConversationsInput!
    $condition: ModelUserConversationsConditionInput
  ) {
    createUserConversations(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      initiatedTime
      duration
      transferDuration
      recordingURL
      requestMeta
      externalConversationId
      status
      conversationPlatform
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateUserConversations = /* GraphQL */ `
  mutation UpdateUserConversations(
    $input: UpdateUserConversationsInput!
    $condition: ModelUserConversationsConditionInput
  ) {
    updateUserConversations(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      initiatedTime
      duration
      transferDuration
      recordingURL
      requestMeta
      externalConversationId
      status
      conversationPlatform
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteUserConversations = /* GraphQL */ `
  mutation DeleteUserConversations(
    $input: DeleteUserConversationsInput!
    $condition: ModelUserConversationsConditionInput
  ) {
    deleteUserConversations(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      initiatedTime
      duration
      transferDuration
      recordingURL
      requestMeta
      externalConversationId
      status
      conversationPlatform
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createUserWhatsappFeedback = /* GraphQL */ `
  mutation CreateUserWhatsappFeedback(
    $input: CreateUserWhatsappFeedbackInput!
    $condition: ModelUserWhatsappFeedbackConditionInput
  ) {
    createUserWhatsappFeedback(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      eventId
      feedback
      feedbackEvent
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateUserWhatsappFeedback = /* GraphQL */ `
  mutation UpdateUserWhatsappFeedback(
    $input: UpdateUserWhatsappFeedbackInput!
    $condition: ModelUserWhatsappFeedbackConditionInput
  ) {
    updateUserWhatsappFeedback(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      eventId
      feedback
      feedbackEvent
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteUserWhatsappFeedback = /* GraphQL */ `
  mutation DeleteUserWhatsappFeedback(
    $input: DeleteUserWhatsappFeedbackInput!
    $condition: ModelUserWhatsappFeedbackConditionInput
  ) {
    deleteUserWhatsappFeedback(input: $input, condition: $condition) {
      id
      userId
      sarathiId
      eventId
      feedback
      feedbackEvent
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createUserReceivedMessages = /* GraphQL */ `
  mutation CreateUserReceivedMessages(
    $input: CreateUserReceivedMessagesInput!
    $condition: ModelUserReceivedMessagesConditionInput
  ) {
    createUserReceivedMessages(input: $input, condition: $condition) {
      id
      userId
      message
      source
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateUserReceivedMessages = /* GraphQL */ `
  mutation UpdateUserReceivedMessages(
    $input: UpdateUserReceivedMessagesInput!
    $condition: ModelUserReceivedMessagesConditionInput
  ) {
    updateUserReceivedMessages(input: $input, condition: $condition) {
      id
      userId
      message
      source
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteUserReceivedMessages = /* GraphQL */ `
  mutation DeleteUserReceivedMessages(
    $input: DeleteUserReceivedMessagesInput!
    $condition: ModelUserReceivedMessagesConditionInput
  ) {
    deleteUserReceivedMessages(input: $input, condition: $condition) {
      id
      userId
      message
      source
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createMultipleChoiceQuestions = /* GraphQL */ `
  mutation CreateMultipleChoiceQuestions(
    $input: CreateMultipleChoiceQuestionsInput!
    $condition: ModelMultipleChoiceQuestionsConditionInput
  ) {
    createMultipleChoiceQuestions(input: $input, condition: $condition) {
      id
      question
      options
      level
      questionNumber
      game
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateMultipleChoiceQuestions = /* GraphQL */ `
  mutation UpdateMultipleChoiceQuestions(
    $input: UpdateMultipleChoiceQuestionsInput!
    $condition: ModelMultipleChoiceQuestionsConditionInput
  ) {
    updateMultipleChoiceQuestions(input: $input, condition: $condition) {
      id
      question
      options
      level
      questionNumber
      game
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteMultipleChoiceQuestions = /* GraphQL */ `
  mutation DeleteMultipleChoiceQuestions(
    $input: DeleteMultipleChoiceQuestionsInput!
    $condition: ModelMultipleChoiceQuestionsConditionInput
  ) {
    deleteMultipleChoiceQuestions(input: $input, condition: $condition) {
      id
      question
      options
      level
      questionNumber
      game
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const createEvent = /* GraphQL */ `
  mutation CreateEvent(
    $input: CreateEventInput!
    $condition: ModelEventConditionInput
  ) {
    createEvent(input: $input, condition: $condition) {
      id
      mainTitle
      subTitle
      hostedBy
      guestSpeaker
      repeat
      slug
      isDeleted
      eventType
      imageUrl
      meetingLink
      description
      maxVisitorsAllowed
      prizeMoney
      eventEndTime
      eventStartTime
      registrationAllowedTillTime
      isPremiumUserOnly
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const updateEvent = /* GraphQL */ `
  mutation UpdateEvent(
    $input: UpdateEventInput!
    $condition: ModelEventConditionInput
  ) {
    updateEvent(input: $input, condition: $condition) {
      id
      mainTitle
      subTitle
      hostedBy
      guestSpeaker
      repeat
      slug
      isDeleted
      eventType
      imageUrl
      meetingLink
      description
      maxVisitorsAllowed
      prizeMoney
      eventEndTime
      eventStartTime
      registrationAllowedTillTime
      isPremiumUserOnly
      createdAt
      updatedAt
      __typename
    }
  }
`;
export const deleteEvent = /* GraphQL */ `
  mutation DeleteEvent(
    $input: DeleteEventInput!
    $condition: ModelEventConditionInput
  ) {
    deleteEvent(input: $input, condition: $condition) {
      id
      mainTitle
      subTitle
      hostedBy
      guestSpeaker
      repeat
      slug
      isDeleted
      eventType
      imageUrl
      meetingLink
      description
      maxVisitorsAllowed
      prizeMoney
      eventEndTime
      eventStartTime
      registrationAllowedTillTime
      isPremiumUserOnly
      createdAt
      updatedAt
      __typename
    }
  }
`;
