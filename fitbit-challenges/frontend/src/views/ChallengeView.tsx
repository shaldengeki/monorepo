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

  let innerContent = <p></p>;
  if (loading) innerContent = <p>Loading...</p>;
  else if (error) innerContent = <p>Error : {error.message}</p>;
  else if (data.challenges.length < 1) {
    innerContent = <p>Error: challenge could not be found!</p>;
  } else if (data.challenges.length > 1) {
    innerContent = <p>Error: multiple challenges with that ID were found!</p>
  } else {
    const challenge = data.challenges[0];
    const users = challenge.users.split(",");
    innerContent = <WorkweekHustle id={id} users={users} createdAt={challenge.createdAt} startAt={challenge.startAt} endAt={challenge.endAt} />;
  }

    return (
      <div className="dark:bg-neutral-600 dark:text-slate-400 h-screen">
        <div className="container mx-auto">
          {innerContent}
        </div>
      </div>
  )
}

export default ChallengeView;
