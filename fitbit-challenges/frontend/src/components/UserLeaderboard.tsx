import React from 'react';
import ProgressBar from './ProgressBar';


export type UserData = {
    name: string;
    value: number;
    unit: string;
}

function getCurrentUnixTime(): number {
    const currentTime = Date.now();
    return Math.round(currentTime / 1000);
}

export function formatDateDifference(seconds: number): string {
    let unit = "";
    let quantity = 0;
    if (seconds < 60) {
        unit = "second";
        quantity = seconds;
    } else if (seconds < 3600) {
        quantity = Math.floor(seconds / 60);
        unit = "minute";
    } else if (seconds < 86400) {
        quantity = Math.floor(seconds / 3600);
        unit = "hour";
    } else if (seconds < 604800) {
        quantity = Math.floor(seconds / 86400);
        unit = "day";
    } else if (seconds < 2592000) {
        quantity = Math.floor(seconds / 604800);
        unit = "week";
    } else if (seconds < 31536000) {
        quantity = Math.floor(seconds / 2592000);
        unit = "month";
    } else {
        quantity = Math.floor(seconds / 31536000);
        unit = "year";
    }

    if (quantity > 1) {
        unit = unit + "s";
    }

    return quantity + " " + unit;
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
        <div>
            <div className='col-span-3 text-center text-2xl'>{title}</div>
            <div className='col-span-3 text-center'>{timingCopy}</div>
        </div>
    );
};

type UserLeaderboardListingEntryProps = {
    user: UserData;
    maximum: number;
}

export const UserLeaderboardListingEntry = ({ user, maximum }: UserLeaderboardListingEntryProps) => {
    return (
        <div className="grid grid-cols-3 gap-0">
            <div className="col-span-2">{user.name}</div>
            <ProgressBar value={user.value} maximum={maximum} />
        </div>
    );
};

type UserLeaderboardListingProps = {
    users: string[];
    userData: UserData[];
    unit: string;
}

const UserLeaderboardListing = ({ users, userData, unit }: UserLeaderboardListingProps) => {
    // Compute the totals per user.
    const userTotals = users.map((user, _) => {
        return {
            'name': user,
            'value': userData.filter(ud => ud.name === user).reduce((acc, curr) => acc + curr.value, 0),
             unit,
        };
    }).sort((a, b) => b.value - a.value);
    const maxValue = Math.max.apply(null, userTotals.map((ud, _) => ud.value));
    const entries = userTotals.map((ud, _) => <UserLeaderboardListingEntry key={ud.name} user={ud} maximum={maxValue} />);

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
    userData: UserData[];
    createdAt: number;
    startAt: number;
    endAt: number;
    unit: string;
}

const UserLeaderboard = ({ challengeName, id, users, userData, createdAt, startAt, endAt, unit }: UserLeaderboardProps) => {
  return (
    <div className="bg-blue-200 dark:bg-indigo-950 dark:text-slate-400 p-2">
        <UserLeaderboardHeader title={challengeName} id={id} startAt={startAt} endAt={endAt} />
        <UserLeaderboardListing users={users} userData={userData} unit={unit} />
    </div>
  )
}

export default UserLeaderboard;
