import * as React from 'react';

import Activity from '../types/Activity';
import StepChallenge from './StepChallenge';

type WorkweekHustleProps = {
    id: number;
    users: string[];
    startAt: number;
    endAt: number;
    ended: boolean;
    sealAt: number;
    sealed: boolean;
    activities: Activity[];
}

const WorkweekHustle = ({id, users, startAt, endAt, ended, sealAt, sealed, activities}: WorkweekHustleProps) => {
    return (
        <StepChallenge
            challengeName={"Workweek Hustle"}
            id={id}
            users={users}
            startAt={startAt}
            endAt={endAt}
            ended={ended}
            sealAt={sealAt}
            sealed={sealed}
            activities={activities}
        />
    );
};

export default WorkweekHustle;
