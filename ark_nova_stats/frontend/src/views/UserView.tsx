import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { useParams } from 'react-router-dom';

import PageTitle from "../components/PageTitle";
import UserInfoBox from '../components/UserInfoBox';
import GameLogsTable from '../components/GameLogsTable';
import GameLog from '../types/GameLog';
import User from '../types/User';
import UserPlayCount from '../types/UserPlayCount';
import LoadingSpinner from '../components/LoadingSpinner';

export const USER_VIEW_QUERY = gql`
    query FetchUser($name: String!) {
        user(name: $name) {
            bgaId
            name
            avatar
            recentGameLogs {
                bgaTableId
                users {
                    bgaId
                    name
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
            numGameLogs
            commonlyPlayedCards {
                card {
                    id
                    bgaId
                    name
                }
                count
            }
            currentElo
            currentArenaElo
        }
    }
`;



type UserViewParams = {
    name: string,
}

const UserView = () => {
    let { name } = useParams<UserViewParams>();
    const { loading, error, data } = useQuery(
        USER_VIEW_QUERY,
        {variables: {name}},
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <LoadingSpinner />;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        const user: User = data.user;
        const commonlyPlayedCards: UserPlayCount[] = data.user.commonlyPlayedCards;
        const recentGameLogs: GameLog[] = data.user.recentGameLogs;
        innerContent = (
            <div>
                <PageTitle linkTo={`/user/${user.name}`}>User: {user.name}</PageTitle>
                <div className={"py-2"}>
                    <UserInfoBox user={user} commonlyPlayedCards={commonlyPlayedCards} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Recent game logs:</h2>
                    <GameLogsTable gameLogs={recentGameLogs} currentPlayer={user} />
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

export default UserView;
