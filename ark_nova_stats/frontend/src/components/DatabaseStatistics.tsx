import React from 'react';

import Stats from '../types/Stats';
import {getDate} from '../DateUtils';

type DatabaseStatisticsParams = {
    stats: Stats | undefined,
}

const DatabaseStatistics = ({stats}: DatabaseStatisticsParams) => {
    let innerContent = <p></p>;
    if (!stats) {
        innerContent = <p>Error: stats could not be retrieved!</p>;
    } else {
        var statsElements = [
            <li>Games recorded: {stats.numGameLogs}</li>,
            <li>Players involved: {stats.numPlayers}</li>
        ];
        if (stats.mostRecentSubmission !== null) {
            statsElements.push(<li>The most recent game was submitted on: {getDate(stats.mostRecentSubmission)}</li>)
        }
        innerContent = <ul className="list-disc">
                {statsElements}
            </ul>;
    }
    return innerContent
}

export default DatabaseStatistics;
