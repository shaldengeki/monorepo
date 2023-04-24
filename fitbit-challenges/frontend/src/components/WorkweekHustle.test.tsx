import { render, screen } from '@testing-library/react';
import WorkweekHustle, { FETCH_ACTIVITIES_QUERY } from './WorkweekHustle';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';


it('should render loading state initially', async () => {
  const testFetchWorkweekHustleQueryMock =   {
    request: {
      query: FETCH_ACTIVITIES_QUERY,
      variables: {
            "users": ['foo', 'bar'],
            "recordedAfter": 0,
            "recordedBefore": 0,
        }
    },
    result: {
      data: {
        activities: []
      }
    }
  };
  render(
    <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
      <WorkweekHustle id={1} users={['foo', 'bar']} createdAt={0} startAt={0} endAt={0} />
    </MockedProvider>,
  );
  expect(await screen.findByText("Loading...")).toBeInTheDocument();
});

it('should render when no activities exist', async () => {
    const testFetchWorkweekHustleQueryMock =   {
      request: {
        query: FETCH_ACTIVITIES_QUERY,
        variables: {
            "users": ['foo', 'bar'],
            "recordedAfter": 0,
            "recordedBefore": 0,
        }
      },
      result: {
        data: {
          activities: []
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
        <WorkweekHustle id={1} users={['foo', 'bar']} createdAt={0} startAt={0} endAt={0} />
      </MockedProvider>,
    );
    expect(await screen.findByText("Workweek Hustle")).toBeInTheDocument();
  });

  it('should select just the latest activity per day', async () => {
    const testFetchWorkweekHustleQueryMock =   {
      request: {
        query: FETCH_ACTIVITIES_QUERY,
        variables: {
            "users": ['foo', 'bar'],
            "recordedAfter": 0,
            "recordedBefore": 0,
        }
      },
      result: {
        data: {
          activities: [
            // User has two records for day 0, one with 1 step, and one with 2 steps.
            {'user': 'foo', 'createdAt': 0, 'recordDate': 0, 'steps': 1, 'activeMinutes': 1, 'distanceKm': 1},
            {'user': 'foo', 'createdAt': 1, 'recordDate': 0, 'steps': 2, 'activeMinutes': 2, 'distanceKm': 2},
          ]
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
        <WorkweekHustle id={1} users={['foo', 'bar']} createdAt={0} startAt={0} endAt={0} />
      </MockedProvider>,
    );
    // user only has 2 steps.
    expect(await screen.findByText("2")).toBeInTheDocument();
  });
