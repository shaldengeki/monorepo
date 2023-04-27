import React from 'react';
import { useQuery, gql } from '@apollo/client';
import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import Challenge from "../types/Challenge";
import {formatDateDifference, getCurrentUnixTime} from '../DateUtils';


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
        <div className="col-span-2 grid grid-cols-3 gap-4 bg-slate-200 px-2 py-4 rounded">
            <div className="col-span-1 text-2xl text-indigo-700">
                <a href={`/challenges/${challenge.id}`}>Workweek Hustle</a>
            </div>
            <div className="col-span-2">
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
        innerContent = (
            <ChallengesListingTable challenges={data.challenges} />
        )
    }

    return (
        <PageContainer>
            <PageTitle>Challenges</PageTitle>
            { innerContent }
        </PageContainer>
    )
}

export default ChallengesListingView;
