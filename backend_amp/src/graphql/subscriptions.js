/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onCreateUser = /* GraphQL */ `
  subscription OnCreateUser($filter: ModelSubscriptionUserFilterInput) {
    onCreateUser(filter: $filter) {
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
export const onUpdateUser = /* GraphQL */ `
  subscription OnUpdateUser($filter: ModelSubscriptionUserFilterInput) {
    onUpdateUser(filter: $filter) {
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
export const onDeleteUser = /* GraphQL */ `
  subscription OnDeleteUser($filter: ModelSubscriptionUserFilterInput) {
    onDeleteUser(filter: $filter) {
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
export const onCreateScheduledJobs = /* GraphQL */ `
  subscription OnCreateScheduledJobs(
    $filter: ModelSubscriptionScheduledJobsFilterInput
  ) {
    onCreateScheduledJobs(filter: $filter) {
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
export const onUpdateScheduledJobs = /* GraphQL */ `
  subscription OnUpdateScheduledJobs(
    $filter: ModelSubscriptionScheduledJobsFilterInput
  ) {
    onUpdateScheduledJobs(filter: $filter) {
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
export const onDeleteScheduledJobs = /* GraphQL */ `
  subscription OnDeleteScheduledJobs(
    $filter: ModelSubscriptionScheduledJobsFilterInput
  ) {
    onDeleteScheduledJobs(filter: $filter) {
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
export const onCreateUserConversations = /* GraphQL */ `
  subscription OnCreateUserConversations(
    $filter: ModelSubscriptionUserConversationsFilterInput
  ) {
    onCreateUserConversations(filter: $filter) {
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
export const onUpdateUserConversations = /* GraphQL */ `
  subscription OnUpdateUserConversations(
    $filter: ModelSubscriptionUserConversationsFilterInput
  ) {
    onUpdateUserConversations(filter: $filter) {
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
export const onDeleteUserConversations = /* GraphQL */ `
  subscription OnDeleteUserConversations(
    $filter: ModelSubscriptionUserConversationsFilterInput
  ) {
    onDeleteUserConversations(filter: $filter) {
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
export const onCreateUserWhatsappFeedback = /* GraphQL */ `
  subscription OnCreateUserWhatsappFeedback(
    $filter: ModelSubscriptionUserWhatsappFeedbackFilterInput
  ) {
    onCreateUserWhatsappFeedback(filter: $filter) {
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
export const onUpdateUserWhatsappFeedback = /* GraphQL */ `
  subscription OnUpdateUserWhatsappFeedback(
    $filter: ModelSubscriptionUserWhatsappFeedbackFilterInput
  ) {
    onUpdateUserWhatsappFeedback(filter: $filter) {
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
export const onDeleteUserWhatsappFeedback = /* GraphQL */ `
  subscription OnDeleteUserWhatsappFeedback(
    $filter: ModelSubscriptionUserWhatsappFeedbackFilterInput
  ) {
    onDeleteUserWhatsappFeedback(filter: $filter) {
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
export const onCreateUserReceivedMessages = /* GraphQL */ `
  subscription OnCreateUserReceivedMessages(
    $filter: ModelSubscriptionUserReceivedMessagesFilterInput
  ) {
    onCreateUserReceivedMessages(filter: $filter) {
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
export const onUpdateUserReceivedMessages = /* GraphQL */ `
  subscription OnUpdateUserReceivedMessages(
    $filter: ModelSubscriptionUserReceivedMessagesFilterInput
  ) {
    onUpdateUserReceivedMessages(filter: $filter) {
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
export const onDeleteUserReceivedMessages = /* GraphQL */ `
  subscription OnDeleteUserReceivedMessages(
    $filter: ModelSubscriptionUserReceivedMessagesFilterInput
  ) {
    onDeleteUserReceivedMessages(filter: $filter) {
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
export const onCreateMultipleChoiceQuestions = /* GraphQL */ `
  subscription OnCreateMultipleChoiceQuestions(
    $filter: ModelSubscriptionMultipleChoiceQuestionsFilterInput
  ) {
    onCreateMultipleChoiceQuestions(filter: $filter) {
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
export const onUpdateMultipleChoiceQuestions = /* GraphQL */ `
  subscription OnUpdateMultipleChoiceQuestions(
    $filter: ModelSubscriptionMultipleChoiceQuestionsFilterInput
  ) {
    onUpdateMultipleChoiceQuestions(filter: $filter) {
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
export const onDeleteMultipleChoiceQuestions = /* GraphQL */ `
  subscription OnDeleteMultipleChoiceQuestions(
    $filter: ModelSubscriptionMultipleChoiceQuestionsFilterInput
  ) {
    onDeleteMultipleChoiceQuestions(filter: $filter) {
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
export const onCreateEvent = /* GraphQL */ `
  subscription OnCreateEvent($filter: ModelSubscriptionEventFilterInput) {
    onCreateEvent(filter: $filter) {
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
export const onUpdateEvent = /* GraphQL */ `
  subscription OnUpdateEvent($filter: ModelSubscriptionEventFilterInput) {
    onUpdateEvent(filter: $filter) {
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
export const onDeleteEvent = /* GraphQL */ `
  subscription OnDeleteEvent($filter: ModelSubscriptionEventFilterInput) {
    onDeleteEvent(filter: $filter) {
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
