import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react';

import PageTitle from "../components/PageTitle";
import Card from '../types/Card';
import User from '../types/User';
import Table from '../components/Table';
import PageLink from '../components/PageLink';
import LoadingSpinner from '../components/LoadingSpinner';

export const CARDS_VIEW_QUERY = gql`
    query FetchCards {
        cards {
            bgaId
            name
            mostPlayedBy(limit:1) {
                user {
                    name
                }
                count
            }
        }
    }
`;

type CardsTableRow = {
    "Name": React.JSX.Element,
    "Most played by": React.JSX.Element,
}

const CardsView = () => {
    const { loading, error, data } = useQuery(
        CARDS_VIEW_QUERY,
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <LoadingSpinner />;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        // @ts-ignore
        const cards: Card[] = data.cards;
        const cardRows: CardsTableRow[] = cards.map((card: Card) => {
        // @ts-ignore
            const mostPlayed = data.cards.find((c: any) => {return c.bgaId === card.bgaId}).mostPlayedBy[0];
            const mostPlayedUser: User = mostPlayed.user;
            return {
                "Name": <PageLink to={`/card/${card.bgaId}`}>{card.name}</PageLink>,
                "Most played by": <PageLink to={`/user/${mostPlayedUser.name}`}>{mostPlayedUser.name} ({mostPlayed.count})</PageLink>
            }
        });
        innerContent = (
            <div className={"py-2"}>
                <Table<CardsTableRow>
                    rows={cardRows}
                    keyName="cards"
                    showFilters={true}
                />
            </div>
        );
    }

    return (
        <div>
            <PageTitle>Cards</PageTitle>
            {innerContent}
        </div>
    )
}

export default CardsView;
