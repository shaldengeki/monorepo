import { render, screen } from '@testing-library/react';
import WorkweekHustle, { getActivityLogs } from './WorkweekHustle';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';


it('should render when no activities exist', async () => {
    render(
        <MockedProvider mocks={[]}>
            <WorkweekHustle
                id={1}
                users={['foo', 'bar']}
                createdAt={0}
                startAt={0}
                endAt={0}
                ended={false}
                sealAt={0}
                sealed={false}
                activities={[]}
            />
        </MockedProvider>,
    );
    expect(await screen.findByText("Workweek Hustle")).toBeInTheDocument();
  });

it('should select just the latest activity per day', async () => {
    const activities = [
        // User has two records for day 0, one with 1 step, and one with 2 steps.
        {'id': 1, 'user': 'foo', 'createdAt': 0, 'recordDate': '1000-11-11', 'steps': 1, 'activeMinutes': 1, 'distanceKm': 1},
        {'id': 2, 'user': 'foo', 'createdAt': 1, 'recordDate': '1000-11-11', 'steps': 2, 'activeMinutes': 2, 'distanceKm': 2},
    ];
    render(
        <MockedProvider mocks={[]}>
        <WorkweekHustle
            id={1}
            users={['foo', 'bar']}
            createdAt={0}
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

describe('getActivityLogs', () => {
    it ('should order results in chronological order', () => {
        expect(getActivityLogs([
            {
                id: 1,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                activeMinutes: 2,
                distanceKm: 2
            },
            {
                id: 2,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1
            },
        ])).toEqual([
            {
                id: 2,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                stepsDelta: 1,
                activeMinutes: 1,
                activeMinutesDelta: 1,
                distanceKm: 1,
                distanceKmDelta: 1
            },
            {
                id: 1,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                stepsDelta: 1,
                activeMinutes: 2,
                activeMinutesDelta: 1,
                distanceKm: 2,
                distanceKmDelta: 1
            },
        ]);
    });
    it ('should remove zero-activity entries', () => {
        expect(getActivityLogs([
            {
                id: 1,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1
            },
            {
                id: 2,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1
            },
        ])).toEqual([
            {
                id: 2,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                stepsDelta: 1,
                activeMinutes: 1,
                activeMinutesDelta: 1,
                distanceKm: 1,
                distanceKmDelta: 1
            },
        ]);
    });
    it ('should correctly identify the prior activity to compare against', () => {
        expect(getActivityLogs([
            {
                id: 1,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1
            },
            {
                id: 2,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                activeMinutes: 2,
                distanceKm: 2
            },
            {
                id: 3,
                user: 'foo',
                createdAt: 2,
                recordDate: '',
                steps: 3,
                activeMinutes: 3,
                distanceKm: 3
            },
        ])).toEqual([
            {
                id: 1,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                stepsDelta: 1,
                activeMinutes: 1,
                activeMinutesDelta: 1,
                distanceKm: 1,
                distanceKmDelta: 1,
            },
            {
                id: 2,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                stepsDelta: 1,
                activeMinutes: 2,
                activeMinutesDelta: 1,
                distanceKm: 2,
                distanceKmDelta: 1,
            },
            {
                id: 3,
                user: 'foo',
                createdAt: 2,
                recordDate: '',
                steps: 3,
                stepsDelta: 1,
                activeMinutes: 3,
                activeMinutesDelta: 1,
                distanceKm: 3,
                distanceKmDelta: 1,
            },
        ]);
        expect(getActivityLogs([
            {
                id: 2,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                activeMinutes: 2,
                distanceKm: 2
            },
            {
                id: 1,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1
            },
            {
                id: 3,
                user: 'foo',
                createdAt: 2,
                recordDate: '',
                steps: 3,
                activeMinutes: 3,
                distanceKm: 3
            },
        ])).toEqual([
            {
                id: 1,
                user: 'foo',
                createdAt: 0,
                recordDate: '',
                steps: 1,
                activeMinutes: 1,
                distanceKm: 1,
                stepsDelta: 1,
                activeMinutesDelta: 1,
                distanceKmDelta: 1,
            },
            {
                id: 2,
                user: 'foo',
                createdAt: 1,
                recordDate: '',
                steps: 2,
                activeMinutes: 2,
                distanceKm: 2,
                stepsDelta: 1,
                activeMinutesDelta: 1,
                distanceKmDelta: 1,
            },
            {
                id: 3,
                user: 'foo',
                createdAt: 2,
                recordDate: '',
                steps: 3,
                activeMinutes: 3,
                distanceKm: 3,
                stepsDelta: 1,
                activeMinutesDelta: 1,
                distanceKmDelta: 1,
            },
        ]);
    });
});
