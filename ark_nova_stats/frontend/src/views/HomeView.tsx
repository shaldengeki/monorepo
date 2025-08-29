import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';

import PageTitle from "../components/PageTitle";
import DatabaseStatistics from '../components/DatabaseStatistics';
import GameLogsTable from '../components/GameLogsTable';
import GameLogArchivesTable from '../components/GameLogArchivesTable';
import Stats from '../types/Stats';
import GameLog from '../types/GameLog';
import GameLogArchive from '../types/GameLogArchive';
import LoadingSpinner from '../../../../react_library/LoadingSpinner';

export const HOME_VIEW_QUERY = gql`
    query FetchHome {
        stats {
            numGameLogs
            numPlayers
            mostRecentSubmission
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
        recentGameLogArchives {
            id
            archiveType
            url
            sizeBytes
            numGameLogs
            numUsers
            maxGameLog {
              bgaTableId
              users {
                name
              }
            }
            createdAt
        }
    }
`;



const HomeView = () => {
    const { loading, error, data } = useQuery(
        HOME_VIEW_QUERY,
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <LoadingSpinner />;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        var stats: Stats = data.stats;
        var gameLogs: GameLog[] = data.recentGameLogs;
        var gameLogArchives: GameLogArchive[] = data.recentGameLogArchives;
        innerContent = (
            <div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Welcome to the database!</h2>
                    <p>There are currently:</p>
                    <DatabaseStatistics stats={stats} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Recently-submitted games:</h2>
                    <GameLogsTable gameLogs={gameLogs} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Recent game log archives:</h2>
                    <GameLogArchivesTable gameLogArchives={gameLogArchives} />
                </div>
            </div>
        );
    }

    return (
        <div>
            <PageTitle linkTo={'/home'}>Home</PageTitle>
            {innerContent}
        </div>
    )
}

export default HomeView;
