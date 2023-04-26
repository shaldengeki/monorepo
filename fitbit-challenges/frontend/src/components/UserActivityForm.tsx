import React from 'react';
import Confetti from './Confetti';
import { useMutation, gql } from '@apollo/client';
import {FETCH_ACTIVITIES_QUERY} from './WorkweekHustle';
import {getCurrentUnixTime} from '../DateUtils';
import Activity, {EmptyActivity} from '../types/Activity';

const CREATE_USER_ACTIVITY_MUTATION = gql`
    mutation CreateUserActivity(
        $user:String!,
        $recordDate:Int!,
        $steps:Int!,
    ) {
        createUserActivity(
            recordDate:$recordDate,
            user:$user,
            steps:$steps,
            activeMinutes:0,
            distanceKm:0
        ) {
            id
            recordDate
            user
            steps
        }
    }
`

const UPDATE_USER_ACTIVITY_MUTATION = gql`
    mutation UpdateUserActivity(
        $id:Int!,
        $user:String!,
        $recordDate:Int!,
        $steps:Int!,
    ) {
        updateUserActivity(
            id:$id,
            recordDate:$recordDate,
            user:$user,
            steps:$steps,
            activeMinutes:0,
            distanceKm:0
        ) {
            id
            recordDate
            user
            steps
        }
    }
`

function padDate(date: number): string {
    let formattedDate = "" + date;
    if (date < 10) {
        formattedDate = "0" + formattedDate;
    }
    return formattedDate;
}

function getDate(time?: number): string {
    let currTime = new Date();
    if (time !== undefined) {
        currTime = new Date(0);
        currTime.setUTCSeconds(time);
    }
    const formattedMonth = padDate(currTime.getMonth() + 1);
    const formattedDate = padDate(currTime.getDate());

    return currTime.getFullYear() + "-" + (formattedMonth) + "-" + formattedDate;
}

function convertDateStringToEpochTime(dateString: string): number {
    return new Date(dateString + "T00:00:00").getTime() / 1000;
}


type MutationErrorDialogProps = {
    error: any
    reset: Function
}

const MutationErrorDialog = ({ error, reset }: MutationErrorDialogProps) => {
    return (
        <dialog className="absolute inset-0" open>
            <p className="text-lg font-bold">Error recording your steps:</p>
            <p>{error.networkError?.message}</p>
            <button
                className="p-0.5 rounded bg-teal-400 dark:bg-pink-900 dark:text-slate-400"
                value="cancel"
                formMethod="dialog"
                onClick={() => reset()}
            >
                Close
            </button>
        </dialog>
    );
}

type MutationSuccessDialogProps = {
    reset: Function
}

const MutationSuccessDialog = ({ reset }: MutationSuccessDialogProps) => {
    return (
        <>
            <dialog className="absolute inset-0" open>
                <p className="text-lg font-bold">🎉Activity logged!🎉</p>
                <button
                    className="p-0.5 rounded bg-teal-400 dark:bg-pink-900 dark:text-slate-400"
                    value="cancel"
                    formMethod="dialog"
                    onClick={() => reset()}
                >
                    Close
                </button>
            </dialog>
            <Confetti />
        </>
    );
}

type UserActivityFormProps = {
    users: string[]
    startAt: number
    endAt: number
    editedActivity: Activity
    editActivityHook: Function
}

const UserActivityForm = ({ users, startAt, endAt, editedActivity, editActivityHook }: UserActivityFormProps) => {
    const [
        createUserActivity,
        {
            data: createUserActivityData,
            loading: createUserActivityLoading,
            error: createUserActivityError,
            reset: createUserActivityReset
        }
    ] = useMutation(
        CREATE_USER_ACTIVITY_MUTATION,
        {
            refetchQueries: [
                {
                    query: FETCH_ACTIVITIES_QUERY,
                    variables: {
                        users,
                        recordedAfter: startAt,
                        recordedBefore: endAt,
                    }
                },
                'FetchActivities'
            ]
        }
    );
    const [
        updateUserActivity,
        {
            data: updateUserActivityData,
            loading: updateUserActivityLoading,
            error: updateUserActivityError,
            reset: updateUserActivityReset
        }
    ] = useMutation(
        UPDATE_USER_ACTIVITY_MUTATION,
        {
            refetchQueries: [
                {
                    query: FETCH_ACTIVITIES_QUERY,
                    variables: {
                        users,
                        recordedAfter: startAt,
                        recordedBefore: endAt,
                    }
                },
                'FetchActivities'
            ]
        }
    );

    if (createUserActivityLoading || updateUserActivityLoading) {
        return <p>Loading...</p>
    }

    const maxDate = endAt > getCurrentUnixTime() ? getCurrentUnixTime() : endAt;

    const id = (editedActivity.id === 0) ? 0 : editedActivity.id;
    const date = (editedActivity.recordDate === "") ? getDate() : editedActivity.recordDate;
    const selectedUser = (editedActivity.user === "") ? users[0] : editedActivity.user;
    const userElements = users.map((user) => {
        if (user === selectedUser) {
            return <option key={user} value={user}>{user}</option>
        } else {
            return <option key={user} value={user}>{user}</option>
        }
    });
    const steps = (editedActivity.steps === 0) ? 0 : editedActivity.steps;

    return <>
        <form
            className="space-x-1"
            onSubmit={e => {
                e.preventDefault();
                if (id !== 0) {
                    updateUserActivity({
                        variables: {
                            id: id,
                            recordDate: convertDateStringToEpochTime(date),
                            user: selectedUser,
                            steps: steps
                        }
                    })
                } else {
                    createUserActivity({
                        variables: {
                            recordDate: convertDateStringToEpochTime(date),
                            user: selectedUser,
                            steps: steps
                        }
                    })
                }
            }}
        >
            <input
                name="id"
                hidden={true}
                value={id}
                readOnly={true}
            />
            <input
                className="rounded p-0.5"
                name="recordDate"
                type="date"
                value={date}
                onChange={(e) => {
                    const updatedActivity = {
                        ...editedActivity,
                        recordDate: e.target.value,
                    }
                    editActivityHook(updatedActivity)
                }}
                max={getDate(maxDate)}
                min={getDate(startAt)}
            />
            <select
                className="rounded p-0.5"
                name="user"
                value={selectedUser}
                onChange={(e) => {
                    const updatedActivity = {
                        ...editedActivity,
                        user: e.target.value
                    }
                    editActivityHook(updatedActivity)
                }}
            >
                {userElements}
            </select>
            <input
                className="rounded p-0.5 w-40"
                name="steps"
                type='number'
                onChange={(e) => {
                    const updatedActivity = {
                        ...editedActivity,
                        steps: parseInt(e.target.value)
                    }
                    editActivityHook(updatedActivity)
                }}
                value={steps}
                placeholder="Today's total steps"
            />
            <button
                className="p-0.5 rounded bg-teal-400 dark:bg-pink-900 dark:text-slate-400"
                type="submit"
            >
                {(id === 0) ? "Log activity" : "Update"}
            </button>
            <button
                className="p-0.5 rounded bg-slate-200 dark:bg-pink-900 dark:text-slate-400"
                onClick={(e) => {e.preventDefault(); editActivityHook(EmptyActivity)}}
            >
                Cancel
            </button>
        </form>
        {
            createUserActivityError &&
                <MutationErrorDialog
                    error={createUserActivityError}
                    reset={createUserActivityReset}
                />
        }
        {
            updateUserActivityError &&
                <MutationErrorDialog
                    error={updateUserActivityError}
                    reset={updateUserActivityReset}
                />
        }
        {
            createUserActivityData &&
                <MutationSuccessDialog
                    reset={createUserActivityReset}
                />
        }
        {
            updateUserActivityData &&
                <MutationSuccessDialog
                    reset={updateUserActivityReset}
                />
        }
    </>;
}

export default UserActivityForm;
