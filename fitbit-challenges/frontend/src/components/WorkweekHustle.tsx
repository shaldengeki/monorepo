import * as React from 'react';
import _ from 'lodash'
import { useQuery, gql } from '@apollo/client';

import Activity, {ActivityDelta} from '../types/Activity';
import UserLeaderboard from './UserLeaderboard';
import UserActivityLog from './UserActivityLog';
import ActivityDataPoint from '../types/ActivityDataPoint';

export const FETCH_ACTIVITIES_QUERY = gql`
    query FetchActivities($users: [String]!, $recordedAfter: Int!, $recordedBefore: Int!) {
        activities(users: $users, recordedBefore: $recordedBefore, recordedAfter: $recordedAfter) {
            id
            user
            createdAt
            recordDate
            steps
            activeMinutes
            distanceKm
        }
    }
`;

export function getLatestActivityPerUserPerDay(activities: Activity[]): Activity[] {
    return _.chain(activities)
        .groupBy(
            (activity: Activity) : string => {
                return activity.user + "|" + activity.recordDate;
            }
        )
        .values()
        .map((activities: Activity[]): Activity => {
            return _.maxBy(activities, 'createdAt') || {
                'id': 0,
                'user': 'unknown',
                'createdAt': 0,
                'recordDate': '',
                'steps': 0,
                'activeMinutes': 0,
                'distanceKm': 0,
            }
        })
        .value();
}

export function getActivityLogs(activities: Activity[]): ActivityDelta[] {
    // Given a list of activity logs,
    // compute the deltas and return them as a list of new activities.
    return _.sortBy(
        activities
            .map((activity: Activity, _: number, allActivities: Activity[]) => {
            // Fetch the prior activity recording for this date.
            const priorActivities = allActivities.filter((priorActivity: Activity): boolean => {
                return (activity.recordDate === priorActivity.recordDate && activity.user === priorActivity.user && activity.createdAt > priorActivity.createdAt);
            }).sort((a: Activity, b: Activity): number => {
                return a.createdAt > b.createdAt ? -1 : 0;
            });
            if (priorActivities.length < 1) {
                // This is the first activity for the day.
                return {
                    ...activity,
                    stepsDelta: activity.steps,
                    activeMinutesDelta: activity.activeMinutes,
                    distanceKmDelta: activity.distanceKm
                };
            } else {
                // There's a prior activity for the day.
                const priorActivity = priorActivities[0];
                return  {
                    ...activity,
                    stepsDelta: (activity.steps - priorActivity.steps),
                    activeMinutesDelta: (activity.activeMinutes - priorActivity.activeMinutes),
                    distanceKmDelta: (activity.distanceKm - priorActivity.distanceKm)
                }
            }
        }).filter((delta: ActivityDelta): boolean => {
            // Filter out any activities with no delta.
            return delta.stepsDelta !== 0;
        }),
        'createdAt'
    );
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
    const leaderboardData: ActivityDataPoint[] = getLatestActivityPerUserPerDay(activities)
        .map((activity: Activity) => {
            return {
                "name": activity.user,
                "value": activity.steps,
                "unit": "steps",
            }
        });

    const activityLogData: ActivityDelta[] = getActivityLogs(activities);

    return (
        <div className="bg-blue-200 dark:bg-indigo-950 dark:text-slate-400 p-2 h-screen flex flex-col">
            <div className="border-b-2 border-slate-50 dark:border-neutral-600 mb-8 pb-4">
                <UserLeaderboard
                    challengeName={"Workweek Hustle"}
                    id={id}
                    users={users}
                    activityData={leaderboardData}
                    createdAt={createdAt}
                    startAt={startAt}
                    endAt={endAt}
                    unit={"steps"}
                />
            </div>
            <UserActivityLog users={users} deltas={activityLogData} startAt={startAt} endAt={endAt} />
        </div>
    );
};

export default WorkweekHustle;
