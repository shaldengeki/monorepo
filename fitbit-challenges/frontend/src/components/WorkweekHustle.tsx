import * as React from 'react';
import { useQuery, gql } from '@apollo/client';

import UserLeaderboard from './UserLeaderboard';
import {UserData} from './UserLeaderboard';

export const FETCH_ACTIVITIES_QUERY = gql`
    query FetchActivities($users: [String]!, $recordedAfter: Int!, $recordedBefore: Int!) {
        activities(users: $users, recordedBefore: $recordedBefore, recordedAfter: $recordedAfter) {
            user
            recordDate
            steps
            activeMinutes
            distanceKm
        }
    }
`;

type Activity = {
    user: string;
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

   const userData: UserData[] = fetchActivities.data.activities.map(
        (activity: Activity) => {
            return {
                "name": activity.user,
                "value": activity.steps,
                "unit": "steps",
            };
        }
    );

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
