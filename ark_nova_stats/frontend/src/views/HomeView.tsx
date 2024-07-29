import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import ExampleComponent from '../components/ExampleComponent';
import Stats from '../types/Stats';
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
    else if (!data.stats || data.stats.length < 1) {
        innerContent = <p>Error: stats could not be retrieved!</p>;
    } else {
        var stats: Stats = data.stats;
        var statsElements = [
            <li>Games recorded: {stats.numGameLogs}</li>,
            <li>Players involved: {stats.numPlayers}</li>
        ];
        if (stats.mostRecentSubmission !== null) {
            statsElements.push(<li>The most recent game was submitted on: {getDate(stats.mostRecentSubmission)}</li>)
        }
        innerContent = (<div>
            <p>Welcome to the database! There are currently:</p>
            <ul className="list-disc">
                {statsElements}
            </ul>
        </div>);
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
