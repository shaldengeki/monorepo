import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import ExampleComponent from '../components/ExampleComponent';
import StatsType from '../types/StatsType';
import {getDate} from '../DateUtils';

export const FETCH_STATS_QUERY = gql`
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
        FETCH_STATS_QUERY,
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else if (data.stats.length < 1) {
        innerContent = <p>Error: stats could not be retrieved!</p>;
    } else {
        var stats: StatsType = data.stats;
        var text = `Welcome to the database! There are currently ${stats.numGameLogs} games recorded across ${stats.numPlayers} players.`
        if (stats.mostRecentSubmission !== null) {
            text += ` The most recent game was submitted on ${getDate(stats.mostRecentSubmission)}.`;
        }
        innerContent = <p>{text}</p>
    }

    return (
        <PageContainer>
            <PageTitle><Link to={'/home'}>Home</Link></PageTitle>
            {innerContent}
            <ExampleComponent />
        </PageContainer>
    )
}

export default HomeView;
