import * as React from 'react';

import Activity from '../types/Activity';
import User from '../types/User';
import StepChallenge from './StepChallenge';

type WeekendWarriorProps = {
    id: number;
    users: User[];
    startAt: number;
    endAt: number;
    ended: boolean;
    sealAt: number;
    sealed: boolean;
    activities: Activity[];
}

const WeekendWarrior = ({id, users, startAt, endAt, ended, sealAt, sealed, activities}: WeekendWarriorProps) => {
    return (
        <StepChallenge
            challengeName={"Weekend Warrior"}
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

export default WeekendWarrior;
