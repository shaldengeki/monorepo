import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import Card from '../types/Card';
import User from '../types/User';
import Table from '../components/Table';

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
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        const cards: Card[] = data.cards;
        const cardRows: CardsTableRow[] = cards.map((card: Card) => {
            const mostPlayed = data.cards.find((c: any) => {return c.bgaId === card.bgaId}).mostPlayedBy[0];
            const mostPlayedUser: User = mostPlayed.user;
            return {
                "Name": <Link to={`/card/${card.bgaId}`}>{card.name}</Link>,
                "Most played by": <Link to={`user/${mostPlayedUser.name}`}>{mostPlayedUser.name} ({mostPlayed.count})</Link>
            }
        });
        innerContent = (
            <div>
                <PageTitle>Cards</PageTitle>
                <div className={"py-2"}>
                    <Table<CardsTableRow>
                        rows={cardRows}
                        key="cards"
                        showFilters={true}
                    />
                </div>
            </div>
        );
    }

    return (
        <PageContainer>
            {innerContent}
        </PageContainer>
    )
}

export default CardsView;