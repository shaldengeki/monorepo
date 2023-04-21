import React from 'react';
import { useQuery, gql } from '@apollo/client';
import { useParams } from 'react-router-dom';
import WorkweekHustle from '../components/WorkweekHustle';

export const FETCH_WORKWEEK_HUSTLE_QUERY = gql`
  query FetchChallenge($id: Int!) {
        challenges(id: $id) {
            id
            users
            createdAt
            startAt
            endAt
        }
    }
`;

type ChallengeViewParams = {
  challengeId: string;
}

const ChallengeView = () => {
  let { challengeId } = useParams<ChallengeViewParams>();
    const id = parseInt(challengeId || "0", 10);

    const  {loading, error, data } = useQuery(
      FETCH_WORKWEEK_HUSTLE_QUERY,
      {variables: { id }},
   );

  if (loading) return <p>Loading...</p>;

  if (error) return <p>Error : {error.message}</p>;

  const challenge = data.challenges[0];
  const users = challenge.users.split(",");

    return (
      <div className="dark:bg-neutral-600 h-screen">
        <div className="container mx-auto">
            <WorkweekHustle id={id} users={users} createdAt={challenge.createdAt} startAt={challenge.startAt} endAt={challenge.endAt} />
        </div>
      </div>
  )
}

export default ChallengeView;
