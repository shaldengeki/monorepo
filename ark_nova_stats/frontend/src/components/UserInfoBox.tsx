import React from 'react';

import User from '../types/User';
import UserPlayCount from '../types/UserPlayCount';
import Table from './Table';
import PageLink from './PageLink';

type UserInfoBoxParams = {
    user: User;
    commonlyPlayedCards: UserPlayCount[];
}

type UserPlayedTableRow = {
    "Card": React.JSX.Element,
    "Count": React.JSX.Element,
}

const UserInfoBox = ({user, commonlyPlayedCards}: UserInfoBoxParams) => {
    let innerContent = <p></p>;
    if (!user) {
        innerContent = <p>Error: user info could not be retrieved!</p>;
    } else if (!commonlyPlayedCards) {
        innerContent = <p>Error: card play info could not be retrieved!</p>;
    } else {
        const rows: UserPlayedTableRow[] = commonlyPlayedCards.map((userPlayCount: UserPlayCount) => {
            return {
                "Card": <PageLink to={"/card/" + userPlayCount.card.bgaId}>{userPlayCount.card.name}</PageLink>,
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
            <Table<UserPlayedTableRow>
                rows={rows}
                key="user-played-cards"
                showFilters={false}
            />
        </div>
    }
    return innerContent
}

export default UserInfoBox;
