import React, {useState} from 'react';
import Activity, {ActivityDelta, EmptyActivity, ActivityTotal} from '../types/Activity';
import {formatDateDifference, getCurrentUnixTime} from '../DateUtils';
import UserActivityForm from './UserActivityForm';

function formatActivityDate(recordDate: string): string {
    const dateObj = new Date(recordDate + "T00:00:00");
    return dateObj.toLocaleDateString(
        undefined,
        {
            weekday: 'long',
        }
    )
}

type PlacementResultEntryProps = {
    totals: ActivityTotal[]
}

const PlacementResultEntry = ({ totals }: PlacementResultEntryProps) => {
    let entryText = `${totals[0].name} won the week with ${totals[0].value} ${totals[0].unit}!`;
    if (totals.length > 1) {
        entryText += ` ${totals[1].name} took second with ${totals[1].value} ${totals[1].unit}.`;
    }
    if (totals.length > 2) {
        entryText += ` ${totals[2].name} came in third with ${totals[2].value} ${totals[2].unit}.`;
    }

    return (
        <div className="grid grid-cols-3 gap-0 mb-7">
            <div className="col-span-3 text-center text-lg">
                {entryText}
            </div>
        </div>
    )
}

type UserActivityLogEntryProps = {
    delta: ActivityDelta
    editHook: Function
}

const UserActivityLogEntry = ( {delta, editHook}: UserActivityLogEntryProps) => {
    return (
        <div className="grid grid-cols-3 gap-0">
            <div className="col-span-2">
                {delta.user} took {delta.stepsDelta} steps on {formatActivityDate(delta.recordDate)}
            </div>
            <div className="col-span-1 text-right italic text-sm">
                <span>
                    {formatDateDifference(getCurrentUnixTime() - delta.createdAt)} ago
                    <button className="text-xs" onClick={() => editHook(delta as Activity)}>✏️</button>
                </span>
            </div>
        </div>
    )
}

type UserActivityLogProps = {
    challengeId: number
    users: string[]
    deltas: ActivityDelta[]
    totals: ActivityTotal[]
    startAt: number
    endAt: number
    sealed: boolean
}

const UserActivityLog = ({ challengeId, users, deltas, totals, startAt, endAt, sealed }: UserActivityLogProps) => {
    const [editedActivity, setEditedActivity] = useState(EmptyActivity);
    const entries = deltas.map(
        (delta: ActivityDelta) => {
            return <UserActivityLogEntry key={delta.id} delta={delta} editHook={setEditedActivity} />;
        }
    )
    return (
        <>
            <div className="grow overflow-y-auto">
                { sealed && <PlacementResultEntry totals={totals} /> }
                {entries}
            </div>
            { !sealed && <div className="border-t-2 border-slate-50 dark:border-neutral-600 mt-8 pt-4">
                <UserActivityForm challengeId={challengeId} users={users} startAt={startAt} endAt={endAt} editedActivity={editedActivity} editActivityHook={setEditedActivity} />
            </div>}
        </>
    )
}

export default UserActivityLog;
