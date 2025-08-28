import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react';
import { useParams } from 'react-router-dom';

import PageTitle from "../components/PageTitle";
import CardInfoBox from '../components/CardInfoBox';
import GameLogsTable from '../components/GameLogsTable';
import Card from '../types/Card';
import GameLog from '../types/GameLog';
import UserPlayCount from '../types/UserPlayCount';
import LoadingSpinner from '../components/LoadingSpinner';

export const USER_VIEW_QUERY = gql`
    query FetchCard($id: String!) {
        card(id: $id) {
            id
            bgaId
            name
            createdAt
            mostPlayedBy {
                user {
                    id
                    bgaId
                    name
                }
                count
            }
            recentGameLogs {
                bgaTableId
                users {
                    bgaId
                    name
                    currentElo
                    currentArenaElo
                }
                gameRatingChanges {
                    user {
                        bgaId
                    }
                    priorElo
                    newElo
                    priorArenaElo
                    newArenaElo
                }
            }
        }
    }
`;



type CardViewParams = {
    id: string,
}

const CardView = () => {
    let { id } = useParams<CardViewParams>();
    const { loading, error, data } = useQuery(
        USER_VIEW_QUERY,
        {variables: {id}},
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <LoadingSpinner />;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        // @ts-ignore
        const card: Card = data.card;
        // @ts-ignore
        const mostPlayedBy: UserPlayCount[] = data.card.mostPlayedBy;
        // @ts-ignore
        const recentGameLogs: GameLog[] = data.card.recentGameLogs;
        innerContent = (
            <div>
                <PageTitle linkTo={`/card/${card.bgaId}`}>Card: {card.name}</PageTitle>
                <div className={"py-2"}>
                    <CardInfoBox card={card} mostPlayedBy={mostPlayedBy} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Recent game logs:</h2>
                    <GameLogsTable gameLogs={recentGameLogs} />
                </div>
            </div>
        );
    }

    return (
        <div>
            {innerContent}
        </div>
    )
}

export default CardView;
