import React, {useState} from 'react';
import { useMutation, useQuery, gql } from '@apollo/client';
import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import Challenge, {emptyChallenge} from "../types/Challenge";
import {formatDateDifference, getCurrentUnixTime, nextMonday} from '../DateUtils';
import { Link } from 'react-router-dom';
import {CancelButton, SubmitButton} from '../components/FormButton';


export const FETCH_CHALLENGES_QUERY = gql`
    query FetchChallenges {
          challenges {
              id
              users
              createdAt
              startAt
              endAt
              ended
              sealAt
              sealed
          }
      }
`;

const CREATE_CHALLENGE_MUTATION = gql`
    mutation CreateChallenge(
        $users:[String]!,
        $startAt:Int!,
    ) {
        createWorkweekHustle(
            users:$users,
            startAt:$startAt,
        ) {
            id
        }
    }
`

type ChallengesListingTableEntryProps = {
    challenge: Challenge
}

const ChallengesListingTableEntry = ({ challenge }: ChallengesListingTableEntryProps) => {
    const users = challenge.users.join(", ")

    const statusText = (challenge.ended || challenge.sealed) ? `ended ${formatDateDifference( getCurrentUnixTime() - challenge.endAt)} ago` : `ends in ${formatDateDifference(challenge.endAt - getCurrentUnixTime())}`

    return (
        <div className="col-span-2 grid grid-cols-3 gap-4 px-2 py-4 rounded bg-slate-200 dark:bg-slate-700">
            <div className="col-span-1 text-2xl text-indigo-700 dark:text-indigo-300">
                <Link to={`/challenges/${challenge.id}`}>Workweek Hustle</Link>
            </div>
            <div className="col-span-2 dark:text-slate-300">
                <p>with {users}</p>
                <p>{statusText}</p>
            </div>
        </div>
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
        <div className="grid grid-cols-3 gap-4">
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
    const [createChallenge, { data, loading, error, reset }] = useMutation(
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

    const joinedUsers = challenge.users.join(",")
    const challengeHook = (e: any) => {
        e.preventDefault();
        createChallenge({
            variables: {
                users: challenge.users,
                startAt: challenge.startAt,
            }
        })
    }
    const cancelHook = (e: any) => {
        e.preventDefault();
        editHook({ ...emptyChallenge, startAt: nextMonday() });
        formHook(false);
    }

    return (
        <div>
            { error && <p>Error creating challenge!</p> }
            { loading && <p>Creating challenge...</p> }
            { !data &&
            <form>
                <input
                    name="users"
                    className="text-slate-800"
                    value={joinedUsers}
                    onChange={(e) => {
                        editHook({
                            ...challenge,
                            users: e.target.value.trim().split(",").map((s) => s.trim()),
                        })
                    }}
                    placeholder="Comma-separated users"
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

    let challenges: Challenge[] = [];
    if (data && data.challenges) {
        challenges = data.challenges.slice(0);
        challenges = challenges.sort((a: Challenge, b: Challenge) => b.endAt - a.endAt);
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/challenges'}>Challenges</Link></PageTitle>
            { loading && <p>Loading...</p> }
            { error && <p>Error: {error.message}</p> }
            <div className="py-2">
                { !editFormShowing && <CreateChallengeLink hook={setEditFormShowing} /> }
                { editFormShowing && <CreateChallengeForm challenge={editedChallenge} editHook={setEditedChallenge} formHook={setEditFormShowing} /> }
            </div>
            { data && data.challenges && data.challenges.length < 1 && <p>No challenges found!</p> }
            { data && data.challenges && <ChallengesListingTable challenges={challenges} /> }
        </PageContainer>
    )
}

export default ChallengesListingView;
