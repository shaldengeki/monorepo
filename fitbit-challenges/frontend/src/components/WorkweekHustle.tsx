import * as React from 'react';
import _ from 'lodash'
import { useQuery, gql } from '@apollo/client';

import UserLeaderboard from './UserLeaderboard';
import {UserData} from './UserLeaderboard';

export const FETCH_ACTIVITIES_QUERY = gql`
    query FetchActivities($users: [String]!, $recordedAfter: Int!, $recordedBefore: Int!) {
        activities(users: $users, recordedBefore: $recordedBefore, recordedAfter: $recordedAfter) {
            user
            createdAt
            recordDate
            steps
            activeMinutes
            distanceKm
        }
    }
`;

type Activity = {
    user: string;
    createdAt: number;
    recordDate: number;
    steps: number;
    activeMinutes: number;
    distanceKm: number;
}

type WorkweekHustleProps = {
    id: number;
    users: string[];
    createdAt: number;
    startAt: number;
    endAt: number;
}

const WorkweekHustle = ({id, users, createdAt, startAt, endAt}: WorkweekHustleProps) => {
   const fetchActivities = useQuery(
        FETCH_ACTIVITIES_QUERY,
        {
            variables: {
                users,
                "recordedAfter": startAt,
                "recordedBefore": endAt,
            }
        }
   )

    if (fetchActivities.loading) return <p>Loading...</p>;

    if (fetchActivities.error) return <p>Error : {fetchActivities.error.message}</p>;

    // There might be many logs for a single date.
    // Retrieve just the latest log for a given date.
    const activities: Activity[] = fetchActivities.data.activities;
    const userData: UserData[] = _.chain(activities)
        .groupBy(
            (activity: Activity) : string => {
                return activity.user + "|" + activity.recordDate.toString();
            }
        )
        .values()
        .map((activities: Activity[]): Activity => {
            return _.maxBy(activities, 'createdAt') || {
                'user': 'unknown',
                'createdAt': 0,
                'recordDate': 0,
                'steps': 0,
                'activeMinutes': 0,
                'distanceKm': 0,
            }
        })
        .map((activity: Activity) => {
            return {
                "name": activity.user,
                "value": activity.steps,
                "unit": "steps",
            }
        })
        .value();

    return (
        <UserLeaderboard
            challengeName={"Workweek Hustle"}
            id={id}
            users={users}
            userData={userData}
            createdAt={createdAt}
            startAt={startAt}
            endAt={endAt}
            unit={"steps"}
        />
    );
};

export default WorkweekHustle;
