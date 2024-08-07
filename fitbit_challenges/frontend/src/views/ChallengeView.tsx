import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { useParams } from 'react-router-dom';
import PageContainer from '../components/PageContainer';
import WorkweekHustle from '../components/WorkweekHustle';
import WeekendWarrior from '../components/WeekendWarrior';
import BingoChallenge from '../components/BingoChallenge';
import Activity from '../types/Activity';
import Challenge, {ChallengeType} from '../types/Challenge';
import User from '../types/User';

export const FETCH_WORKWEEK_HUSTLE_QUERY = gql`
    query FetchChallenge($id: Int!) {
          challenges(id: $id) {
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
              activities {
                id
                user
                createdAt
                recordDate
                steps
                activeMinutes
                distanceKm
              }
          }
          currentUser {
            fitbitUserId
            displayName
            createdAt
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
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else if (data.challenges.length < 1) {
        innerContent = <p>Error: challenge could not be found!</p>;
    } else if (data.challenges.length > 1) {
        innerContent = <p>Error: multiple challenges with that ID were found!</p>
    } else {
        const challenges: Challenge[] = data.challenges;
        const challenge = challenges[0];
        const activities: Activity[] = challenge.activities;
        const currentUser: User = data.currentUser;

        if (challenge.challengeType === ChallengeType.WeekendWarrior) {
            innerContent = <WeekendWarrior
                id={id}
                users={challenge.users}
                startAt={challenge.startAt}
                endAt={challenge.endAt}
                ended={challenge.ended}
                sealAt={challenge.sealAt}
                sealed={challenge.sealed}
                activities={activities}
            />;
        } else if (challenge.challengeType === ChallengeType.WorkweekHustle) {
            innerContent = <WorkweekHustle
                id={id}
                users={challenge.users}
                startAt={challenge.startAt}
                endAt={challenge.endAt}
                ended={challenge.ended}
                sealAt={challenge.sealAt}
                sealed={challenge.sealed}
                activities={activities}
            />;
        } else if (challenge.challengeType === ChallengeType.Bingo) {
            innerContent = <BingoChallenge id={id} currentUser={currentUser} />;
        } else {
            return <p>Invalid challenge type!</p>
        }
    }

    return (
        <PageContainer>
            {innerContent}
        </PageContainer>
    )
}

export default ChallengeView;
