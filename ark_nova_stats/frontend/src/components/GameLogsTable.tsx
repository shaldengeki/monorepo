import React from 'react';
import { Link } from 'react-router-dom';

import GameLog from '../types/GameLog';
import User from '../types/User';
import Table from './Table';

type GameLogsTableParams = {
    gameLogs: GameLog[];
    currentPlayer?: User;
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
            const rowAttrs: any = {
                "BGA table": <Link to={"https://boardgamearena.com/table?table=" + gameLog.bgaTableId}>{gameLog.bgaTableId}</Link>,
                "Players": <ul>{gameLog.users.map((user: User) => {return <li><Link to={`/user/${user.name}`}>{user.name}</Link></li>})}</ul>,
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
        <Table
            cols={tableColumns}
            rows={rows}
            key="game-logs"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogsTable;
