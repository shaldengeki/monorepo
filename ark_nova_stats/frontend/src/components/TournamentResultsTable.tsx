import React from 'react';

import GameStatistics from '../types/GameStatistics';
import Table from './Table';
import PageLink from './PageLink';
import _ from 'lodash';

type TournamentResultsTableParams = {
    statistics: GameStatistics[];
}

type TournamentResultsTableRow = {
    "Player": React.JSX.Element,
    "Wins": React.JSX.Element,
    "Losses": React.JSX.Element,
    "Overall": React.JSX.Element,

}

type TournamentPlayerRecord = {
    user: string,
    wins: number,
    losses: number,
    total: number,
}

const TournamentResultsTable = ({statistics}: TournamentResultsTableParams) => {
    let innerContent = <p></p>;
    if (!statistics || statistics.length < 1) {
        innerContent = <p>Error: tournament results could not be retrieved!</p>;
    } else {
        const sortedInputStats = [...statistics].sort((a, b) => {
            return (a.user.bgaId < b.user.bgaId) ? -1 : (a.user.bgaId === b.user.bgaId) ? 0 : 1;
        })
        const transformedData = sortedInputStats.map((stat: GameStatistics) => {
            return {user: stat.user.name, win: Boolean(stat.rank === 1), loss: Boolean(stat.rank !== 1)};
        })
        const groupedData = _.groupBy(transformedData, (obj) => obj.user);
        const groupedEntries = _.toPairs(groupedData);
        const summedData = groupedEntries.map(([user, records]) => {
            const initialRecord: TournamentPlayerRecord = {
                user: user,
                wins: 0,
                losses: 0,
                total: 0
            }
            return (records || []).reduce(
                (prev, curr) => {
                    if (curr.win) {
                        prev.wins++;
                        prev.total++;
                    } else if (curr.loss) {
                        prev.losses++;
                        prev.total--;
                    }
                    return prev;
                },
                initialRecord
            )
        })
        var rows: TournamentResultsTableRow[] = summedData.map((record: TournamentPlayerRecord) => {
            return {
                "Player": <p>{record.user}</p>,
                "Wins": <p>{record.wins}</p>,
                "Losses": <p>{record.losses}</p>,
                "Overall": <p>{(record.total > 0) ? `+${record.total}` : record.total}</p>,
            }
        });

        innerContent = (
            <Table<TournamentResultsTableRow>
                rows={rows}
                key="tournament-results"
                showFilters={true}
            />
        );
    }
    return innerContent
}

export default TournamentResultsTable;
