import * as React from 'react';

import UserLeaderboard from './UserLeaderboard';

type WorkweekHustleProps = {
    id: number;
    users: string[];
    createdAt: number;
    startAt: number;
    endAt: number;
}

const WorkweekHustle = ({id, users, createdAt, startAt, endAt}: WorkweekHustleProps) => {
    return (
        <div>
            <UserLeaderboard challengeName={"Workweek Hustle"} id={id} users={users} createdAt={createdAt} startAt={startAt} endAt={endAt} />
        </div>
    );
};

export default WorkweekHustle;
