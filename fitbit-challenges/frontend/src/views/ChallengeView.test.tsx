import { render, screen } from '@testing-library/react';
import ChallengeView from './ChallengeView';
import { FETCH_WORKWEEK_HUSTLE_QUERY } from './ChallengeView';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render loading state initially', async () => {
  const testFetchWorkweekHustleQueryMock =   {
    request: {
      query: FETCH_WORKWEEK_HUSTLE_QUERY,
      variables: {
          id: 0
      },
    },
    result: {
      data: {
        challenges: []
      }
    }
  };
  render(
    <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
      <ChallengeView />
    </MockedProvider>,
  );
  expect(await screen.findByText("Loading...")).toBeInTheDocument();
});

it('should handle when the challenge does not exist', async () => {
    const testFetchWorkweekHustleQueryMock =   {
      request: {
        query: FETCH_WORKWEEK_HUSTLE_QUERY,
        variables: {
            id: 0
        },
      },
      result: {
        data: {
          challenges: []
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
        <ChallengeView />
      </MockedProvider>,
    );
    expect(await screen.findByText("Error: challenge could not be found!")).toBeInTheDocument();
  });


it('should handle when multiple challenges are found', async () => {
    const testChallenge = {
        id: 1,
        challengeType: 0,
        users: "a,b,c",
        createdAt: 1,
        startAt: 1,
        endAt: 1,
        ended: false,
        sealAt: 0,
        sealed: false,
        activities: []
    }
    const testFetchWorkweekHustleQueryMock =   {
      request: {
        query: FETCH_WORKWEEK_HUSTLE_QUERY,
        variables: {
            id: 0
        },
      },
      result: {
        data: {
          challenges: [testChallenge, testChallenge]
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock]}>
        <ChallengeView />
      </MockedProvider>,
    );
    expect(await screen.findByText("Error: multiple challenges with that ID were found!")).toBeInTheDocument();
  });
