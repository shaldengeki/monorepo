import React from 'react';

import Card from '../types/Card';
import UserPlayCount from '../types/UserPlayCount';
import Table from '../../../../react_library/Table';
import PageLink from './PageLink';

type CardInfoBoxParams = {
    card: Card;
    mostPlayedBy: UserPlayCount[];
}

type CardPlayedTableRow = {
    "User": React.JSX.Element,
    "Count": React.JSX.Element,
}

const CardInfoBox = ({card, mostPlayedBy}: CardInfoBoxParams) => {
    let innerContent = <p></p>;
    if (!card) {
        innerContent = <p>Error: card info could not be retrieved!</p>;
    } else if (!mostPlayedBy) {
        innerContent = <p>Error: card play info could not be retrieved!</p>;
    } else {
        const rows: CardPlayedTableRow[] = mostPlayedBy.map((userPlayCount: UserPlayCount) => {
            return {
                "User": <PageLink to={"/user/" + userPlayCount.user.name}>{userPlayCount.user.name}</PageLink>,
                "Count": <ul>{userPlayCount.count}</ul>,
            }
        });

        innerContent = <div>
            <ul>
                <li>BGA ID: {card.bgaId}</li>
            </ul>
            <h2 className={"text-xl"}>Most played by:</h2>
            <Table<CardPlayedTableRow>
                rows={rows}
                keyName="card-played-cards"
                showFilters={false}
            />
        </div>
    }
    return innerContent
}

export default CardInfoBox;
