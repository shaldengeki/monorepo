import React from 'react';
import { useMutation, gql } from '@apollo/client';
import {FETCH_ACTIVITIES_QUERY} from './WorkweekHustle';
import {getCurrentUnixTime} from '../DateUtils';

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
        currTime = new Date(time * 1000);
    }
    const formattedMonth = padDate(currTime.getMonth() + 1);
    const formattedDate = padDate(currTime.getDate());

    return currTime.getFullYear() + "-" + (formattedMonth) + "-" + formattedDate;
}

type UserActivityFormProps = {
    users: string[]
    startAt: number
    endAt: number
}

const UserActivityForm = ({ users, startAt, endAt }: UserActivityFormProps) => {
    const [createUserActivity, {data, loading, error, reset}] = useMutation(
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

    const maxDate = endAt > getCurrentUnixTime() ? getCurrentUnixTime() : endAt;

    let recordDate: any;
    let user: any;
    let steps: any;

    if (loading) {
        return <p>Loading...</p>
    }
    const userElements = users.map((user) => {
        return <option key={user} value={user}>{user}</option>
    });

    return <>
        <form
            className="space-x-1"
            onSubmit={e => {
                e.preventDefault();
                const enteredRecordDate = recordDate ? Date.parse(recordDate.value) / 1000 : 0;
                const enteredUser = user ? user.value : "";
                const enteredSteps = parseInt(steps ? steps.value : "0", 10);
                createUserActivity({
                    variables: {
                        recordDate: enteredRecordDate,
                        user: enteredUser,
                        steps: enteredSteps
                    }
                })
            }}
        >
            <input
                className="rounded p-0.5"
                type="date"
                ref={node => {
                    recordDate = node;
                }}
                defaultValue={getDate()}
                max={getDate(maxDate)}
                min={getDate(startAt)}
            />
            <select
                className="rounded p-0.5"
                ref={node => {
                    user = node;
                }}>
                {userElements}
            </select>
            <input
                type='number'
                className="rounded p-0.5 w-40"
                ref={node => {
                    steps = node;
                }}
                placeholder="Today's total steps"
            />
            <button
                className="p-0.5 rounded bg-teal-400 dark:bg-pink-900 dark:text-slate-400"
                type="submit"
            >
                Log activity
            </button>
        </form>
        {
            error && <dialog className="absolute inset-0" open>
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
        }
        {
            data && <dialog className="absolute inset-0" open>
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
        }
    </>;
}

export default UserActivityForm;
