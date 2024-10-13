/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getUser = /* GraphQL */ `
  query GetUser($id: ID!) {
    getUser(id: $id) {
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
export const listUsers = /* GraphQL */ `
  query ListUsers(
    $filter: ModelUserFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listUsers(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        firstName
        lastName
        gender
        status
        isDeleted
        interestedInClubSukoon
        dateOfBirth
        mobileNumber
        createdAt
        updatedAt
        __typename
      }
      nextToken
      __typename
    }
  }
`;
export const getUserNotification = /* GraphQL */ `
  query GetUserNotification($id: ID!) {
    getUserNotification(id: $id) {
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
export const listUserNotifications = /* GraphQL */ `
  query ListUserNotifications(
    $filter: ModelUserNotificationFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listUserNotifications(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const getScheduledJobs = /* GraphQL */ `
  query GetScheduledJobs($id: ID!) {
    getScheduledJobs(id: $id) {
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
export const listScheduledJobs = /* GraphQL */ `
  query ListScheduledJobs(
    $filter: ModelScheduledJobsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listScheduledJobs(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const getUserConversations = /* GraphQL */ `
  query GetUserConversations($id: ID!) {
    getUserConversations(id: $id) {
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
export const listUserConversations = /* GraphQL */ `
  query ListUserConversations(
    $filter: ModelUserConversationsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listUserConversations(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const getUserWhatsappFeedback = /* GraphQL */ `
  query GetUserWhatsappFeedback($id: ID!) {
    getUserWhatsappFeedback(id: $id) {
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
export const listUserWhatsappFeedbacks = /* GraphQL */ `
  query ListUserWhatsappFeedbacks(
    $filter: ModelUserWhatsappFeedbackFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listUserWhatsappFeedbacks(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const getUserReceivedMessages = /* GraphQL */ `
  query GetUserReceivedMessages($id: ID!) {
    getUserReceivedMessages(id: $id) {
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
export const listUserReceivedMessages = /* GraphQL */ `
  query ListUserReceivedMessages(
    $filter: ModelUserReceivedMessagesFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listUserReceivedMessages(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
        id
        userId
        message
        source
        createdAt
        updatedAt
        __typename
      }
      nextToken
      __typename
    }
  }
`;
export const getMultipleChoiceQuestions = /* GraphQL */ `
  query GetMultipleChoiceQuestions($id: ID!) {
    getMultipleChoiceQuestions(id: $id) {
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
export const listMultipleChoiceQuestions = /* GraphQL */ `
  query ListMultipleChoiceQuestions(
    $filter: ModelMultipleChoiceQuestionsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listMultipleChoiceQuestions(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const getEvent = /* GraphQL */ `
  query GetEvent($id: ID!) {
    getEvent(id: $id) {
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
export const listEvents = /* GraphQL */ `
  query ListEvents(
    $filter: ModelEventFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listEvents(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const userByMobileNumber = /* GraphQL */ `
  query UserByMobileNumber(
    $mobileNumber: String!
    $sortDirection: ModelSortDirection
    $filter: ModelUserFilterInput
    $limit: Int
    $nextToken: String
  ) {
    userByMobileNumber(
      mobileNumber: $mobileNumber
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
        id
        firstName
        lastName
        gender
        status
        isDeleted
        interestedInClubSukoon
        dateOfBirth
        mobileNumber
        createdAt
        updatedAt
        __typename
      }
      nextToken
      __typename
    }
  }
`;
export const userNotificationsByUserId = /* GraphQL */ `
  query UserNotificationsByUserId(
    $userId: ID!
    $sortDirection: ModelSortDirection
    $filter: ModelUserNotificationFilterInput
    $limit: Int
    $nextToken: String
  ) {
    userNotificationsByUserId(
      userId: $userId
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const scheduledJobsByStatusAndTime = /* GraphQL */ `
  query ScheduledJobsByStatusAndTime(
    $scheduledJobStatus: ScheduledJobStatus!
    $scheduledJobTime: ModelStringKeyConditionInput
    $sortDirection: ModelSortDirection
    $filter: ModelScheduledJobsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    scheduledJobsByStatusAndTime(
      scheduledJobStatus: $scheduledJobStatus
      scheduledJobTime: $scheduledJobTime
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const userConversationsByUserId = /* GraphQL */ `
  query UserConversationsByUserId(
    $userId: ID!
    $sortDirection: ModelSortDirection
    $filter: ModelUserConversationsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    userConversationsByUserId(
      userId: $userId
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
export const userConversationsBySarathiId = /* GraphQL */ `
  query UserConversationsBySarathiId(
    $sarathiId: ID!
    $sortDirection: ModelSortDirection
    $filter: ModelUserConversationsFilterInput
    $limit: Int
    $nextToken: String
  ) {
    userConversationsBySarathiId(
      sarathiId: $sarathiId
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
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
      nextToken
      __typename
    }
  }
`;
