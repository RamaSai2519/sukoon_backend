/* eslint-disable */
// this is an auto generated file. This will be overwritten

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
