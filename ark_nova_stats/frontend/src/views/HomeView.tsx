import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import DatabaseStatistics from '../components/DatabaseStatistics';
import GameLogsTable from '../components/GameLogsTable';
import Stats from '../types/Stats';
import GameLog from '../types/GameLog';

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
                name
            }
        }
    }
`;



type HomeViewParams = {
}

const HomeView = () => {
    const { loading, error, data } = useQuery(
        HOME_VIEW_QUERY,
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        var stats: Stats = data.stats;
        var gameLogs: GameLog[] = data.recentGameLogs;
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
            </div>
        );
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/home'}>Home</Link></PageTitle>
            {innerContent}
        </PageContainer>
    )
}

export default HomeView;
