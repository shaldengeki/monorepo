import React from 'react';
import { Link } from 'react-router-dom';

import GameLog from '../types/GameLog';
import User from '../types/User';
import Table from './Table';

type GameLogsTableParams = {
    gameLogs: GameLog[];
}

const GameLogsTable = ({gameLogs}: GameLogsTableParams) => {
    let innerContent = <p></p>;
    if (!gameLogs) {
        innerContent = <p>Error: game logs could not be retrieved!</p>;
    } else {

        var rows = gameLogs.map((gameLog: GameLog) => {
            return {
                "BGA table": <Link to={"https://boardgamearena.com/table?table=" + gameLog.bgaTableId}>{gameLog.bgaTableId}</Link>,
                "Players": gameLog.users.map((user: User) => {return <Link to={`/user/${user.name}`}>user.name</Link>}).sort().join(", ")
            }
        });
        innerContent = (
        <Table
            cols={["BGA table", "Players"]}
            rows={rows}
            key="game-logs"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogsTable;
