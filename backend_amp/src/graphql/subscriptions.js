/* eslint-disable */
// this is an auto generated file. This will be overwritten

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
