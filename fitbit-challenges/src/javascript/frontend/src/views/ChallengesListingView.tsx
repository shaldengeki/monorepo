import React, {useState} from 'react';
import { useMutation, useQuery, gql } from '@apollo/client';
import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import Challenge, {ChallengeType, emptyChallenge} from "../types/Challenge";
import {formatDateDifference, getCurrentUnixTime, getDate, nextMonday, nextSaturday, today} from '../DateUtils';
import { Link } from 'react-router-dom';
import {CancelButton, SubmitButton} from '../components/FormButton';
import User from '../types/User';

export const FETCH_CHALLENGES_QUERY = gql`
    query FetchChallenges {
        currentUser {
            activeChallenges {
                id
                challengeType
                users {
                  fitbitUserId
                  displayName
                }
                createdAt
                startAt
                endAt
                ended
                sealAt
                sealed
            }
            pastChallenges {
                id
                challengeType
                users {
                  fitbitUserId
                  displayName
                }
                createdAt
                startAt
                endAt
                ended
                sealAt
                sealed
            }
        }
    }
`;

export const FETCH_USERS_QUERY = gql`
      query FetchUsers {
        users {
            displayName
            fitbitUserId
        }
      }
`;

const CREATE_CHALLENGE_MUTATION = gql`
    mutation CreateChallenge(
        $users:[String]!,
        $challengeType:Int!,
        $startAt:Int!,
        $endAt:Int,
    ) {
        createChallenge(
            users:$users,
            challengeType:$challengeType,
            startAt:$startAt,
            endAt:$endAt,
        ) {
            id
        }
    }
`

type ChallengesListingTableEntryProps = {
    challenge: Challenge
}

const ChallengesListingTableEntry = ({ challenge }: ChallengesListingTableEntryProps) => {
    const users = challenge.users.map((user) => { return user.displayName; }).join(", ")

    const statusText = (challenge.ended || challenge.sealed) ? `ended ${formatDateDifference( getCurrentUnixTime() - challenge.endAt)} ago` : `ends in ${formatDateDifference(challenge.endAt - getCurrentUnixTime())}`
    let challengeName = "Workweek Hustle"
    if (challenge.challengeType === ChallengeType.WeekendWarrior) {
        challengeName = "Weekend Warrior"
    } else if (challenge.challengeType === ChallengeType.Bingo) {
        challengeName = "Bingo"
    }

    return (
        <Link to={`/challenges/${challenge.id}`} className="col-span-2 grid grid-cols-4 gap-4 px-2 py-4 rounded bg-slate-200 dark:bg-slate-700">
            <div className="col-span-2 text-2xl text-indigo-700 dark:text-indigo-300">
                {challengeName}
            </div>
            <div className="col-span-2 dark:text-slate-300">
                <p>with {users}</p>
                <p>{statusText}</p>
            </div>
        </Link>
    )
}

type ChallengesListingTableProps = {
    challenges: Challenge[]
}

const ChallengesListingTable = ({ challenges }: ChallengesListingTableProps) => {
    const entries = challenges.map((challenge: Challenge) => {
        return <ChallengesListingTableEntry challenge={challenge} />;
    });
    return (
        <div className="grid grid-cols-2 gap-4">
            {entries}
        </div>
    )
}

type CreateChallengeLinkProps = {
    hook: Function
}

const CreateChallengeLink = ({ hook }: CreateChallengeLinkProps) => {
    return (
        <SubmitButton hook={(e: any) => {e.preventDefault(); hook(true);}}>
            Create challenge
        </SubmitButton>
    )
}

type CreateChallengeFormProps = {
    challenge: Challenge
    editHook: Function
    formHook: Function
}

const CreateChallengeForm = ({ challenge, editHook, formHook }: CreateChallengeFormProps) => {
    const [createChallenge, { data: createChallengeData, loading: createChallengeLoading, error: createChallengeError }] = useMutation(
        CREATE_CHALLENGE_MUTATION,
        {
            refetchQueries: [
                {
                    query: FETCH_CHALLENGES_QUERY,
                },
                'FetchChallenges'
            ]
        }
    )

    const { data: fetchUsersData, loading: fetchUsersLoading, error: fetchUsersError } = useQuery(FETCH_USERS_QUERY);

    const challengeHook = (e: any) => {
        e.preventDefault();
        let startAt = 0;
        if (challenge.challengeType === ChallengeType.WeekendWarrior) {
            startAt = nextSaturday();
        } else if (challenge.challengeType === ChallengeType.WorkweekHustle) {
            startAt = nextMonday();
        } else if (challenge.challengeType === ChallengeType.Bingo) {
            startAt = challenge.startAt;
        }
        let endAt = null;
        console.log("challenge", challenge);
        if (challenge.challengeType === ChallengeType.Bingo) {
            endAt = challenge.endAt;
        }
        console.log("endAt", endAt)
        // We don't guard against wrong challenge types, because the API should handle this for us.
        createChallenge({
            variables: {
                users: challenge.users,
                challengeType: challenge.challengeType,
                startAt: startAt,
                endAt: endAt,
            }
        })
    }
    const cancelHook = (e: any) => {
        e.preventDefault();
        editHook(emptyChallenge);
        formHook(false);
    }
    const challengeElements = [
        <option key={0} value={0}>Workweek Hustle</option>,
        <option key={1} value={1}>Weekend Warrior</option>,
        <option key={2} value={2}>Bingo</option>
    ]
    let userElements: JSX.Element[] = [];
    if (fetchUsersData) {
        userElements = fetchUsersData.users.map((user: User) => {
            return <option key={user.fitbitUserId} value={user.fitbitUserId}>{user.displayName}</option>
        })
    }
    const startAt = (challenge.startAt === 0) ? getDate(today()) : getDate(challenge.startAt);

    return (
        <div>
            { createChallengeError && <p>Error creating challenge!</p> }
            { createChallengeLoading && <p>Creating challenge...</p> }
            { !createChallengeData &&
            <form>
                { fetchUsersLoading && <span>Loading users...</span>}
                { fetchUsersError && <span>Error loading users!</span>}
                { fetchUsersData &&
                    <select
                        className="rounded p-0.5"
                        name="users"
                        multiple
                        onChange={(e) => {
                            let users = [];
                            for (let i = 0; i < e.target.selectedOptions.length; i++) {
                                users.push(e.target.selectedOptions[i].value);
                            }
                            editHook({
                                ...challenge,
                                users
                            })
                        }}
                    >
                        {userElements}
                    </select>
                }
                <select
                    className="rounded p-0.5"
                    name="challengeType"
                    value={challenge.challengeType}
                    onChange={(e) => {
                        editHook({
                            ...challenge,
                            challengeType: parseInt(e.target.value),
                        })
                    }}
                >
                    {challengeElements}
                </select>
                <input
                    className="rounded p-0.5"
                    name="startAt"
                    type="date"
                    value={startAt}
                    onChange={(e) => {
                        editHook({
                            ...challenge,
                            startAt: e.target.value,
                        })
                    }}
                    min={startAt}
                />
                <input
                    className="rounded p-0.5"
                    name="days"
                    type="number"
                    onChange={(e) => {
                        const endAt = challenge.startAt + (24*60*60*parseInt(e.target.value, 10));
                        console.log("endAt", endAt);
                        editHook({
                            ...challenge,
                            endAt: endAt,
                        });
                    }}
                    min={1}
                    max={100}
                    size={3}
                />
                <SubmitButton hook={challengeHook}>
                    Submit
                </SubmitButton>
                <CancelButton hook={cancelHook}>
                    Cancel
                </CancelButton>
            </form> }
        </div>
    )
}

const ChallengesListingView = () => {
    const { loading, error, data } = useQuery(
        FETCH_CHALLENGES_QUERY,
    );

    const [editFormShowing, setEditFormShowing] = useState(false);
    const [editedChallenge, setEditedChallenge] = useState({ ...emptyChallenge, startAt: nextMonday() });

    let activeChallenges: Challenge[] = [];
    let pastChallenges: Challenge[] = [];
    if (data && data.currentUser && data.currentUser.activeChallenges) {
        activeChallenges = data.currentUser.activeChallenges;
    }
    if (data && data.currentUser && data.currentUser.pastChallenges) {
        pastChallenges = data.currentUser.pastChallenges;
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/challenges'}>Challenges</Link></PageTitle>
            <div className="py-2">
                <h1 className="text-2xl py-2">Start a challenge</h1>
                { !editFormShowing && <CreateChallengeLink hook={setEditFormShowing} /> }
                { editFormShowing && <CreateChallengeForm challenge={editedChallenge} editHook={setEditedChallenge} formHook={setEditFormShowing} /> }
            </div>
            <div>
                { loading && <p>Loading...</p> }
                { error && <p>Error: {error.message}</p> }
                <div className="py-4 border-b-2 border-slate-50 dark:border-neutral-600">
                    <h1 className="text-2xl py-2">Current challenges</h1>
                    { activeChallenges.length < 1 && <p>No current challenges found!</p> }
                    { activeChallenges.length >= 1 &&
                        <ChallengesListingTable challenges={activeChallenges} />
                    }
                </div>
                <div className="py-4">
                    <h1 className="text-2xl py-2">Past challenges</h1>
                    { pastChallenges.length < 1 && <p>No prior challenges found!</p> }
                    { pastChallenges.length >= 1 &&
                        <ChallengesListingTable challenges={pastChallenges} />
                    }

                </div>
            </div>
        </PageContainer>
    )
}

export default ChallengesListingView;
