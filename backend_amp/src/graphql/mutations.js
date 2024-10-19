/* eslint-disable */
// this is an auto generated file. This will be overwritten

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
