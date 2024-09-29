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
    query FetchCards() {
        cards {
            bgaId
            name
            mostPlayedBy {
                user {
                    name
                }
                count
            }
        }
    }
`;



const CardsView = () => {
    const { loading, error, data } = useQuery(
        CARDS_VIEW_QUERY,
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        const cards: Card[] = data.cards;
        const tableColumns = ["Name", "Most played by"];
        const cardRows = cards.map((card: Card) => {
            const mostPlayedUser: User = data.cards.find((c: any) => {return c.bgaId === card.bgaId}).mostPlayedBy[0];
            return {
                "Name": <Link to={`/card/${card.bgaId}`}>{card.name}</Link>,
                "Most played by": <Link to={`user/${mostPlayedUser.name}`}>{mostPlayedUser.name}</Link>
            }
        });
        innerContent = (
            <div>
                <PageTitle>Cards</PageTitle>
                <div className={"py-2"}>
                    <Table
                        cols={tableColumns}
                        rows={cardRows}
                        key="cards"
                        showFilters={false}
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
