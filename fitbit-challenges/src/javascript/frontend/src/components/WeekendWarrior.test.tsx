import { render, screen } from '@testing-library/react';
import WeekendWarrior from './WeekendWarrior';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';


it('should render when no activities exist', async () => {
    render(
        <MockedProvider mocks={[]}>
            <WeekendWarrior
                id={1}
                users={['foo', 'bar']}
                startAt={0}
                endAt={0}
                ended={false}
                sealAt={0}
                sealed={false}
                activities={[]}
            />
        </MockedProvider>,
    );
    expect(await screen.findByText("Weekend Warrior")).toBeInTheDocument();
  });

it('should select just the latest activity per day', async () => {
    const activities = [
        // User has two records for day 0, one with 1 step, and one with 2 steps.
        {'id': 1, 'user': 'foo', 'createdAt': 0, 'recordDate': '1000-11-11', 'steps': 1, 'activeMinutes': 1, 'distanceKm': 1},
        {'id': 2, 'user': 'foo', 'createdAt': 1, 'recordDate': '1000-11-11', 'steps': 2, 'activeMinutes': 2, 'distanceKm': 2},
    ];
    render(
        <MockedProvider mocks={[]}>
        <WeekendWarrior
            id={1}
            users={['foo', 'bar']}
            startAt={0}
            endAt={0}
            ended={false}
            sealAt={0}
            sealed={false}
            activities={activities}
        />
        </MockedProvider>,
    );
    // user only has 2 steps.
    expect(await screen.findByText("2")).toBeInTheDocument();
});
