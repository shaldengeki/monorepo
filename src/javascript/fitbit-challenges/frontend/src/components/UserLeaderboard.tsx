import React from 'react';
import ProgressBar from './ProgressBar';
import {ActivityTotal} from '../types/Activity';
import {getCurrentUnixTime, formatDateDifference} from '../DateUtils';
import PageTitle from "../components/PageTitle";

export type UserData = {
    name: string;
    value: number;
    unit: string;
}

export type UserLeaderboardHeaderProps = {
    title: string;
    id: number;
    startAt: number;
    endAt: number;
    ended: boolean;
    sealAt: number;
    sealed: boolean;
}

export const UserLeaderboardHeader = ({ title, id, startAt, endAt, ended, sealAt, sealed }: UserLeaderboardHeaderProps) => {
    let timingCopy = "";
    if (ended) {
        timingCopy = "Ended " + formatDateDifference(getCurrentUnixTime() - endAt) + " ago";
        if (!sealed) {
            timingCopy = "⚠️" + timingCopy + `. ${formatDateDifference(sealAt - getCurrentUnixTime())} left to record data!⚠️`
        }
    } else if (getCurrentUnixTime() > startAt) {
        timingCopy = "Started " + formatDateDifference(getCurrentUnixTime() - startAt) + " ago (ends in " + formatDateDifference(endAt - getCurrentUnixTime()) + ")";
    } else {
        timingCopy = "Will start in " + formatDateDifference(startAt - getCurrentUnixTime());
    }
    return (
        <div>
            <PageTitle className="col-span-3 text-center">
                <a href={`/challenges/${id}`}>{title}</a>
            </PageTitle>
            <div className='col-span-3 text-center text-xl dark:text-slate-300'>{timingCopy}</div>
        </div>
    );
};

type UserLeaderboardListingEntryProps = {
    activityTotal: ActivityTotal;
    maximum: number;
    sealed: boolean;
    rank: number;
}

export const UserLeaderboardListingEntry = ({ activityTotal, maximum, sealed, rank }: UserLeaderboardListingEntryProps) => {
    let placeEmoji = "";
    if (sealed) {
        if (rank === 1) {
            placeEmoji = "🥇";
        } else if (rank === 2) {
            placeEmoji = "🥈";
        } else if (rank === 3) {
            placeEmoji = "🥉";
        }
    }
    return (
        <div className="grid grid-cols-3 gap-0">
            <div className="col-span-2">{placeEmoji}{activityTotal.name}</div>
            <ProgressBar value={activityTotal.value} maximum={maximum} />
        </div>
    );
};

type UserLeaderboardListingProps = {
    activityTotals: ActivityTotal[];
    unit: string;
    sealed: boolean;
}

const UserLeaderboardListing = ({ activityTotals, unit, sealed }: UserLeaderboardListingProps) => {
    const maxValue = Math.max.apply(null, activityTotals.map((at, _) => at.value));
    const entries = activityTotals.map((at, idx) => <UserLeaderboardListingEntry key={at.name} activityTotal={at} maximum={maxValue} sealed={sealed} rank={idx + 1} />);

    return (
        <div>
            {entries}
        </div>
    )
}

type UserLeaderboardProps = {
    challengeName: string;
    id: number;
    activityTotals: ActivityTotal[];
    startAt: number;
    endAt: number;
    ended: boolean;
    sealAt: number;
    sealed: boolean;
    unit: string;
}

const UserLeaderboard = ({ challengeName, id, activityTotals, startAt, endAt, ended, sealAt, sealed, unit }: UserLeaderboardProps) => {
  return (
    <div>
        <UserLeaderboardHeader title={challengeName} id={id} startAt={startAt} endAt={endAt} ended={ended} sealAt={sealAt} sealed={sealed} />
        <UserLeaderboardListing activityTotals={activityTotals} unit={unit} sealed={sealed} />
    </div>
  )
}

export default UserLeaderboard;
