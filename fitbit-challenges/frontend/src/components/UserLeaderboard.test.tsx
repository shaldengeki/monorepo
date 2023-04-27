import { render, screen } from '@testing-library/react';
import { UserLeaderboardListingEntry } from './UserLeaderboard';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import {ActivityTotal} from "../types/Activity";

it('should have the username and steps in the entry', async () => {
  const at: ActivityTotal = {
    name: "test-username",
    value: 5728,
    unit: "steps",
  }
  const maxSteps = 6173;
  render(
    <MockedProvider mocks={[]}>
      <UserLeaderboardListingEntry key={"key"} activityTotal={at} maximum={maxSteps} sealed={false} rank={1} />
    </MockedProvider>,
  );
  expect(await screen.findByText("test-username")).toBeInTheDocument();
  expect(await screen.findByText("5728")).toBeInTheDocument();
});
