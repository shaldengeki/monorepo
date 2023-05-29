import { getActivityLogs } from './StepChallenge';
import React from 'react';

const users = [
    {'fitbitUserId': 'foo', 'displayName': 'foo', 'createdAt': 0, 'activities': []},
    {'fitbitUserId': 'bar', 'displayName': 'bar', 'createdAt': 0, 'activities': []},
];

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
        ], users)).toEqual([
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
        ], users)).toEqual([
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
        ], users)).toEqual([
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
        ], users)).toEqual([
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
