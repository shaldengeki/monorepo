import { render, screen } from '@testing-library/react';
import { UserLeaderboardListingEntry } from './UserLeaderboard';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should have the username and steps in the entry', async () => {
  const user = {
    "name": "test-username",
    "steps": 5728,
  }
  const maxSteps = 6173;
  render(
    <MockedProvider mocks={[]}>
      <UserLeaderboardListingEntry key={"key"} user={user} maxSteps={maxSteps} />
    </MockedProvider>,
  );
  expect(await screen.findByText("test-username")).toBeInTheDocument();
  expect(await screen.findByText("5728")).toBeInTheDocument();
});
