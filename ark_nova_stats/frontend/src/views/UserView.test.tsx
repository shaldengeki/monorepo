import { render, screen } from '@testing-library/react';
import UserView from './UserView';
import { USER_VIEW_QUERY } from './UserView';
import { emptyUser } from '../types/User';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'

it('should render view when empty data is returned', async () => {
  const testFetchStatsMock = {
    request: {
      query: USER_VIEW_QUERY
    },
    result: {
      data: {
        user: emptyUser,
      }
    }
  }

  render(
      <MockedProvider mocks={[testFetchStatsMock]}>
        <UserView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("User:")).toBeInTheDocument();
});
