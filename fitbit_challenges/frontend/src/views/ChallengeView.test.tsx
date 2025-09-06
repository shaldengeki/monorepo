import { render, screen } from '@testing-library/react';
import ChallengeView from './ChallengeView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import { emptyUser } from '../types/User';
import { FETCH_CURRENT_USER_QUERY, FETCH_WORKWEEK_HUSTLE_QUERY } from '../queries';

const testFetchCurrentUserMock = {
  request: {
    query: FETCH_CURRENT_USER_QUERY
  },
  result: {
    data: {
      currentUser: null
    }
  }
}

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
          challenges: [],
          currentUser: emptyUser
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock, testFetchCurrentUserMock]}>
        <ChallengeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Error: challenge could not be found!")).toBeInTheDocument();
  });


it('should handle when multiple challenges are found', async () => {
    const testChallenge = {
        id: 1,
        challengeType: 0,
        users: [
          {fitbitUserId: 'a', displayName: 'A'},
          {fitbitUserId: 'b', displayName: 'B'},
          {fitbitUserId: 'c', displayName: 'C'},
        ],
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
          challenges: [testChallenge, testChallenge],
          currentUser: emptyUser
        }
      }
    };
    render(
      <MockedProvider mocks={[testFetchWorkweekHustleQueryMock, testFetchCurrentUserMock]}>
        <ChallengeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Error: multiple challenges with that ID were found!")).toBeInTheDocument();
  });
