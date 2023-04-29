import React from 'react';
import { useQuery, gql } from '@apollo/client';
import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import Challenge from "../types/Challenge";
import {formatDateDifference, getCurrentUnixTime} from '../DateUtils';
import { Link } from 'react-router-dom';


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

const ChallengesListingView = () => {
    const { loading, error, data } = useQuery(
        FETCH_CHALLENGES_QUERY,
    );

    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else if (data.challenges.length < 1) {
        innerContent = <p>No challenges found!</p>;
    } else {
        const challenges: Challenge[] = data.challenges;
        const sortedChallenges = challenges.sort((a, b) => b.endAt - a.endAt);
        innerContent = (
            <ChallengesListingTable challenges={sortedChallenges} />
        )
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/challenges'}>Challenges</Link></PageTitle>
            { innerContent }
        </PageContainer>
    )
}

export default ChallengesListingView;
