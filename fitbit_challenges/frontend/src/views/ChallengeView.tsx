import { useQuery } from '@apollo/client/react';
import { useParams } from 'react-router-dom';
import WorkweekHustle from '../components/WorkweekHustle';
import WeekendWarrior from '../components/WeekendWarrior';
import BingoChallenge from '../components/BingoChallenge';
import Activity from '../types/Activity';
import Challenge, {ChallengeType} from '../types/Challenge';
import User from '../types/User';
import { FETCH_WORKWEEK_HUSTLE_QUERY } from '../queries';

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
    else if (error) return <p>Error: {error.message}</p>;
    else if (data.challenges.length < 1) {
        return <p>Error: challenge could not be found!</p>;
    } else if (data.challenges.length > 1) {
        return <p>Error: multiple challenges with that ID were found!</p>
    } else {
        const challenges: Challenge[] = data.challenges;
        const challenge = challenges[0];
        const activities: Activity[] = challenge.activities;
        const currentUser: User = data.currentUser;

        if (challenge.challengeType === ChallengeType.WeekendWarrior) {
            return <WeekendWarrior
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
            return <WorkweekHustle
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
            return <BingoChallenge id={id} currentUser={currentUser} />;
        } else {
            return <p>Invalid challenge type!</p>
        }
    }
}

export default ChallengeView;
