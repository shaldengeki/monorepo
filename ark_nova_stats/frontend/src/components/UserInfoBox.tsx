import React from 'react';
import { Link } from 'react-router-dom';

import GameLog from '../types/GameLog';
import User from '../types/User';
import Table from './Table';

type UserInfoBoxParams = {
    user: User;
}

const UserInfoBox = ({user}: UserInfoBoxParams) => {
    let innerContent = <p></p>;
    if (!user) {
        innerContent = <p>Error: user info could not be retrieved!</p>;
    } else {
        innerContent = <ul>
            <li>BGA ID: {user.bgaId}</li>
            <li>Number of games archived: {user.numGameLogs}</li>
        </ul>
    }
    return innerContent
}

export default UserInfoBox;
