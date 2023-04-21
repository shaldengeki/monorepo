import React from 'react';
import ProgressBar from './ProgressBar';

type UserLeaderboardHeaderProps = {
    title: string;
    id: number;
    startAt: number;
    endAt: number;
}

function getCurrentUnixTime(): number {
    const currentTime = Date.now();
    return Math.round(currentTime / 1000);
}

function formatDateDifference(seconds: number): string {
    if (seconds < 60) {
        return seconds + " seconds";
    } else if (seconds < 3600) {
        return Math.floor(seconds / 60) + " minutes";
    } else if (seconds < 86400) {
        return Math.floor(seconds / 3600) + " hours";
    } else if (seconds < 604800) {
        return Math.floor(seconds / 86400) + " days";
    } else if (seconds < 2592000) {
        return Math.floor(seconds / 604800) + " weeks";
    } else if (seconds < 31536000) {
        return Math.floor(seconds / 2592000) + " months";
    } else {
        return Math.floor(seconds / 31536000) + " years";
    }
}

const UserLeaderboardHeader = ({ title, id, startAt, endAt }: UserLeaderboardHeaderProps) => {
    console.log("current time: " + getCurrentUnixTime());
    console.log("start at: " + startAt);

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

type User = {
    name: string;
    steps: number;
}

type UserLeaderboardListingEntryProps = {
    user: User;
    maxSteps: number;
}

export const UserLeaderboardListingEntry = ({ user, maxSteps }: UserLeaderboardListingEntryProps) => {
    return (
        <div className="grid grid-cols-3 gap-0">
            <div className="col-span-2">{user.name}</div>
            <ProgressBar value={user.steps} maximum={maxSteps} />
        </div>
    );
};

type UserLeaderboardListingProps = {
    users: string[];
}

const UserLeaderboardListing = ({ users }: UserLeaderboardListingProps) => {
    const MAX_STEPS = 17284;
    const fakeStepData = users.map(
        (user, _) => { return {"name": user, "steps": Math.floor(Math.random() * MAX_STEPS)}; }
    ).sort((a, b) => b['steps'] - a['steps'])

    const maxSteps = Math.max.apply(null, fakeStepData.map((user, _) => user['steps']))
    const entries = fakeStepData.map((user, _) => <UserLeaderboardListingEntry key={user.name} user={user} maxSteps={maxSteps} />);

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
    createdAt: number;
    startAt: number;
    endAt: number;
}

const UserLeaderboard = ({ challengeName, id, users, createdAt, startAt, endAt }: UserLeaderboardProps) => {
  return (
    <div className="bg-blue-200 p-2">
        <UserLeaderboardHeader title={challengeName} id={id} startAt={startAt} endAt={endAt} />
        <UserLeaderboardListing users={users} />
    </div>
  )
}

export default UserLeaderboard;
