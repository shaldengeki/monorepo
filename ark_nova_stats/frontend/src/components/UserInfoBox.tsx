import React from 'react';
import { Link } from 'react-router-dom';

import User from '../types/User';
import UserPlayCount from '../types/UserPlayCount';
import Table from './Table';

type UserInfoBoxParams = {
    user: User;
    commonlyPlayedCards: UserPlayCount[];
}

const UserInfoBox = ({user, commonlyPlayedCards}: UserInfoBoxParams) => {
    let innerContent = <p></p>;
    if (!user) {
        innerContent = <p>Error: user info could not be retrieved!</p>;
    } else if (!commonlyPlayedCards) {
        innerContent = <p>Error: card play info could not be retrieved!</p>;
    } else {
        const rows = commonlyPlayedCards.map((userPlayCount: UserPlayCount) => {
            return {
                "Card": <Link to={"/card/" + userPlayCount.card.bgaId}>{userPlayCount.card.name}</Link>,
                "Count": <ul>{userPlayCount.count}</ul>,
            }
        });

        innerContent = <div>
            <ul>
                <li>BGA ID: {user.bgaId}</li>
                <li>Number of games archived: {user.numGameLogs}</li>
                <li>Current ELO: {user.currentElo}</li>
                <li>Current Arena ELO: {user.currentArenaElo}</li>
            </ul>
            <h2 className={"text-xl"}>Most played:</h2>
            <Table
                cols={["Card", "Count"]}
                rows={rows}
                key="user-played-cards"
                showFilters={false}
            />
        </div>
    }
    return innerContent
}

export default UserInfoBox;
