import React from 'react';

import GameLog from '../types/GameLog';
import User from '../types/User';
import Table from './Table';
import PageLink from './PageLink';

type GameLogsTableParams = {
    gameLogs: GameLog[];
    currentPlayer?: User;
}

type GameLogsTableRow = {
    "BGA table": React.JSX.Element,
    "Players": React.JSX.Element,
    "Rating changes"?: React.JSX.Element,
}

const GameLogsTable = ({gameLogs, currentPlayer}: GameLogsTableParams) => {
    let innerContent = <p></p>;
    if (!gameLogs) {
        innerContent = <p>Error: game logs could not be retrieved!</p>;
    } else {
        const tableColumns = ["BGA table", "Players"];
        if (currentPlayer !== undefined) {
            tableColumns.push("Rating changes")
        }

        var rows = gameLogs.map((gameLog: GameLog) => {
            const rowAttrs: GameLogsTableRow = {
                "BGA table": <PageLink to={"https://boardgamearena.com/table?table=" + gameLog.bgaTableId}>{gameLog.bgaTableId}</PageLink>,
                "Players": <ul>{gameLog.users.map((user: User) => {
                    const ratingChange = gameLog.gameRatingChanges.find((change) => { return change.user.bgaId === user.bgaId })
                    return <li><PageLink to={`/user/${user.name}`}>{user.name} ({ratingChange?.priorElo} / {ratingChange?.priorArenaElo})</PageLink></li>;
                })}</ul>,
            }
            if (currentPlayer !== undefined) {
                const ratingChange = gameLog.gameRatingChanges.find((change) => { return change.user.bgaId === currentPlayer.bgaId })
                if (ratingChange !== undefined) {
                    rowAttrs["Rating changes"] = <ul>
                    <li>Normal: {ratingChange?.priorElo} -&gt; {ratingChange?.newElo}</li>
                    <li>Arena: {ratingChange?.priorArenaElo} -&gt; {ratingChange?.newArenaElo}</li>
                    </ul>;
                }
            }

            return rowAttrs;
        });
        innerContent = (
        <Table<GameLogsTableRow>
            rows={rows}
            key="game-logs"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogsTable;
