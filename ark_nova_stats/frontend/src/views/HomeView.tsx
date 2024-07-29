import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import DatabaseStatistics from '../components/DatabaseStatistics';
import Stats from '../types/Stats';

export const HOME_VIEW_QUERY = gql`
    query FetchStats {
        stats {
            numGameLogs
            numPlayers
            mostRecentSubmission
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
        innerContent = <DatabaseStatistics stats={stats} />
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/home'}>Home</Link></PageTitle>
            {innerContent}
        </PageContainer>
    )
}

export default HomeView;
