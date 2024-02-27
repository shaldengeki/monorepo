import { render, screen } from '@testing-library/react';
import { UserLeaderboardHeader, UserLeaderboardListingEntry } from './UserLeaderboard';
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
  expect(await screen.findByText("5,728")).toBeInTheDocument();

});

it('should not show time left to record data when the challenge is not sealable', async () => {
  render(
    <MockedProvider mocks={[]}>
      <UserLeaderboardHeader
        title={"Test header"}
        id={1}
        startAt={0}
        endAt={0}
        ended={true}
        sealAt={0}
        sealed={true}
      />
    </MockedProvider>,
  );
  expect(screen.queryByText("left to record data", {exact: false})).not.toBeInTheDocument();
});
