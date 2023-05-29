import * as React from 'react';
import _ from 'lodash'

import Activity, {ActivityDelta} from '../types/Activity';
import User from '../types/User';
import UserLeaderboard from './UserLeaderboard';
import UserActivityLog from './UserActivityLog';
import {ActivityTotal, emptyActivity} from '../types/Activity';

export function getLatestActivityPerUserPerDay(activities: Activity[]): Activity[] {
    // There might be many logs for a single date.
    // Retrieve just the latest log for a given date.
    return _.chain(activities)
        .groupBy(
            (activity: Activity) : string => {
                return activity.user + "|" + activity.recordDate;
            }
        )
        .values()
        .map((activities: Activity[]): Activity => {
            return _.maxBy(activities, 'createdAt') || emptyActivity;
        })
        .value();
}

export function getActivityLogs(activities: Activity[], users: User[]): ActivityDelta[] {
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
            const selectedUser = users.filter((user) => { return user.fitbitUserId === activity.user })[0];
            if (priorActivities.length < 1) {
                // This is the first activity for the day.
                return {
                    ...activity,
                    stepsDelta: activity.steps,
                    activeMinutesDelta: activity.activeMinutes,
                    distanceKmDelta: activity.distanceKm,
                    user: selectedUser.displayName,
                };
            } else {
                // There's a prior activity for the day.
                const priorActivity = priorActivities[0];
                return  {
                    ...activity,
                    stepsDelta: (activity.steps - priorActivity.steps),
                    activeMinutesDelta: (activity.activeMinutes - priorActivity.activeMinutes),
                    distanceKmDelta: (activity.distanceKm - priorActivity.distanceKm),
                    user: selectedUser.displayName,
                }
            }
        }).filter((delta: ActivityDelta): boolean => {
            // Filter out any activities with no delta.
            return delta.stepsDelta !== 0;
        }),
        'createdAt'
    );
}

type StepChallengeProps = {
    challengeName: string;
    id: number;
    users: User[];
    startAt: number;
    endAt: number;
    ended: boolean;
    sealAt: number;
    sealed: boolean;
    activities: Activity[];
}

const StepChallenge = ({challengeName, id, users, startAt, endAt, ended, sealAt, sealed, activities}: StepChallengeProps) => {
    // Compute the totals per user.
    const totalData: ActivityTotal[] = getLatestActivityPerUserPerDay(activities)
        .map((activity: Activity) => {
            const selectedUser = users.filter((user) => { return user.fitbitUserId === activity.user; })[0];
            return {
                "name": selectedUser.displayName,
                "value": activity.steps,
                "unit": "steps",
            }
        });

    const activityTotals = users.map((user, _) => {
        return {
            name: user.displayName,
            value: totalData.filter(at => at.name === user.displayName).reduce((acc, curr) => acc + curr.value, 0),
            unit: "steps",
        };
    }).sort((a, b) => b.value - a.value);

    const activityLogData: ActivityDelta[] = getActivityLogs(activities, users);

    return (
        <>
            <div className="border-b-2 border-slate-50 dark:border-neutral-600 mb-8 pb-4">
                <UserLeaderboard
                    challengeName={challengeName}
                    id={id}
                    activityTotals={activityTotals}
                    startAt={startAt}
                    endAt={endAt}
                    ended={ended}
                    sealAt={sealAt}
                    sealed={sealed}
                    unit={"steps"}
                />
            </div>
            <UserActivityLog challengeId={id} users={users} deltas={activityLogData} totals={activityTotals} startAt={startAt} endAt={endAt} sealed={sealed} />
        </>
    );
};

export default StepChallenge;
