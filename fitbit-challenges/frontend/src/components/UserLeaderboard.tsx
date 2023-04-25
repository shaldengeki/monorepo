import React from 'react';
import ProgressBar from './ProgressBar';
import ActivityDataPoint from '../types/ActivityDataPoint';
import {getCurrentUnixTime, formatDateDifference} from '../DateUtils';

export type UserData = {
    name: string;
    value: number;
    unit: string;
}

type UserLeaderboardHeaderProps = {
    title: string;
    id: number;
    startAt: number;
    endAt: number;
}

const UserLeaderboardHeader = ({ title, id, startAt, endAt }: UserLeaderboardHeaderProps) => {
    let timingCopy = "";
    if (getCurrentUnixTime() > endAt) {
        timingCopy = "Ended " + formatDateDifference(getCurrentUnixTime() - endAt) + " ago";
    } else if (getCurrentUnixTime() > startAt) {
        timingCopy = "Started " + formatDateDifference(getCurrentUnixTime() - startAt) + " ago (ends in " + formatDateDifference(endAt - getCurrentUnixTime()) + ")";
    } else {
        timingCopy = "Will start in " + formatDateDifference(startAt - getCurrentUnixTime());
    }
    return (
        <div className="border-b-2 border-slate-50 dark:border-neutral-600 mb-8 pb-4">
            <div className='col-span-3 text-center text-2xl'>{title}</div>
            <div className='col-span-3 text-center'>{timingCopy}</div>
        </div>
    );
};

type UserLeaderboardListingEntryProps = {
    activityDataPoint: ActivityDataPoint;
    maximum: number;
}

export const UserLeaderboardListingEntry = ({ activityDataPoint, maximum }: UserLeaderboardListingEntryProps) => {
    return (
        <div className="grid grid-cols-3 gap-0">
            <div className="col-span-2">{activityDataPoint.name}</div>
            <ProgressBar value={activityDataPoint.value} maximum={maximum} />
        </div>
    );
};

type UserLeaderboardListingProps = {
    users: string[];
    activityData: ActivityDataPoint[];
    unit: string;
}

const UserLeaderboardListing = ({ users, activityData, unit }: UserLeaderboardListingProps) => {
    // Compute the totals per user.
    const userTotals = users.map((user, _) => {
        return {
            'name': user,
            'value': activityData.filter(adp => adp.name === user).reduce((acc, curr) => acc + curr.value, 0),
             unit,
        };
    }).sort((a, b) => b.value - a.value);
    const maxValue = Math.max.apply(null, userTotals.map((adp, _) => adp.value));
    const entries = userTotals.map((adp, _) => <UserLeaderboardListingEntry key={adp.name} activityDataPoint={adp} maximum={maxValue} />);

    return (
        <div>
            {entries}
        </div>
    )
}

type UserLeaderboardProps = {
    challengeName: string;
    id: number;
    users: string[];
    activityData: ActivityDataPoint[];
    createdAt: number;
    startAt: number;
    endAt: number;
    unit: string;
}

const UserLeaderboard = ({ challengeName, id, users, activityData, createdAt, startAt, endAt, unit }: UserLeaderboardProps) => {
  return (
    <div>
        <UserLeaderboardHeader title={challengeName} id={id} startAt={startAt} endAt={endAt} />
        <UserLeaderboardListing users={users} activityData={activityData} unit={unit} />
    </div>
  )
}

export default UserLeaderboard;
