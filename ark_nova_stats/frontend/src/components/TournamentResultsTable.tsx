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
    "Ties": React.JSX.Element,
    "Overall": React.JSX.Element,

}

type TournamentPlayerRecord = {
    user: string,
    wins: number,
    losses: number,
    ties: number,
    total: number,
}

const computeGameResults = (statistics: GameStatistics[]): TournamentPlayerRecord[] => {
    // First, group by table ID, so we can detect ties.
    const statsByGame = _.toPairs(_.groupBy(statistics, (stat) => stat.gameLog?.bgaTableId));
    const gameResults = statsByGame.flatMap(([_unused, stats]) => {
        if (stats.filter((s) => s.rank === 1).length == stats.length) {
            // This is a tie.
            return stats.map((stat) => {
                return {user: stat.user.name, wins: 0, losses: 0, ties: 1, total: 0};
            })
        }
        // Not a tie; we can use the ranks directly.
        // TODO: specify the total here directly, and just add it up later.
        return stats.map((stat) => {
            return {user: stat.user.name, wins: + Boolean(stat.rank === 1), losses: + Boolean(stat.rank > 1), ties: 0, total: 0};
        })
    });
    return gameResults;
}

const computePlayerScores = (statistics: GameStatistics[]) => {
    const gameResults = computeGameResults(statistics);
    const groupedResults = _.toPairs(_.groupBy(gameResults, (obj) => obj.user));
    const totalResults = groupedResults.map(([user, records]) => {
        const initialRecord: TournamentPlayerRecord = {
            user: user,
            wins: 0,
            losses: 0,
            ties: 0,
            total: 0
        }
        return (records || []).reduce(
            (prev, curr) => {
                prev.wins += curr.wins;
                prev.losses += curr.losses;
                prev.ties += curr.ties;

                if (curr.wins) {
                    prev.total++;
                } else if (curr.losses) {
                    prev.total--;
                }
                return prev;
            },
            initialRecord
        )
    })
    const sortedResults = totalResults.sort((a, b) => {
        // Order by total score first.
        if (a.total > b.total) {
            return -1
        }
        if (a.total < b.total ) {
            return 1
        }
        // Tiebreak by total wins.
        if (a.wins > b.wins) {
            return -1
        }
        if (a.wins < b.wins) {
            return 1
        }
        // Tiebreak by time violations.
        // We can't do this (yet); we don't expose time data.
        return 0;
    });

    return sortedResults;
}

const TournamentResultsTable = ({statistics}: TournamentResultsTableParams) => {
    let innerContent = <p></p>;
    if (!statistics || statistics.length < 1) {
        innerContent = <p>Error: tournament results could not be retrieved!</p>;
    } else {
        const sortedResults = computePlayerScores(statistics);
        var rows: TournamentResultsTableRow[] = sortedResults.map((record: TournamentPlayerRecord) => {
            return {
                "Player": <PageLink to={`/user/${record.user}`}>{record.user}</PageLink>,
                "Wins": <p>{record.wins}</p>,
                "Losses": <p>{record.losses}</p>,
                "Ties": <p>{record.ties}</p>,
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
