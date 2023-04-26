import React, {useState} from 'react';
import Activity, {ActivityDelta, EmptyActivity} from '../types/Activity';
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
    users: string[]
    deltas: ActivityDelta[]
    startAt: number
    endAt: number
}

const UserActivityLog = ({ users, deltas, startAt, endAt }: UserActivityLogProps) => {
    const [editedActivity, setEditedActivity] = useState(EmptyActivity);
    const entries = deltas.map(
        (delta: ActivityDelta) => {
            return <UserActivityLogEntry key={delta.id} delta={delta} editHook={setEditedActivity} />;
        }
    )
    return (
        <>
            <div className="grow overflow-y-auto">
                {entries}
            </div>
            <div className="border-t-2 border-slate-50 dark:border-neutral-600 mt-8 pt-4">
                <UserActivityForm users={users} startAt={startAt} endAt={endAt} editedActivity={editedActivity} editActivityHook={setEditedActivity} />
            </div>
        </>
    )
}

export default UserActivityLog;
