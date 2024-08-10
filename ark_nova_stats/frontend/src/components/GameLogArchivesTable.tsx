import React from 'react';
import { Link } from 'react-router-dom';

import {getDate} from '../DateUtils';
import GameLogArchive from '../types/GameLogArchive';
import User from '../types/User';
import Table from './Table';

type GameLogArchivesTableParams = {
    gameLogArchives: GameLogArchive[];
}

const GameLogArchivesTable = ({gameLogArchives}: GameLogArchivesTableParams) => {
    let innerContent = <p></p>;
    if (!gameLogArchives) {
        innerContent = <p>Error: game log archives could not be retrieved!</p>;
    } else {
        var rows = gameLogArchives.map((gameLogArchive: GameLogArchive) => {
            let latestTableDescription = <Link to={"https://boardgamearena.com/table?table=" + gameLogArchive.maxGameLog.bgaTableId}>
                {gameLogArchive.maxGameLog.bgaTableId}
            </Link>;
            return {
                "Link": <Link to={gameLogArchive.url}>Download</Link>,
                "Date": getDate(gameLogArchive.createdAt),
                "Type": gameLogArchive.archiveType,
                "Games": gameLogArchive.numGameLogs,
                "Users": gameLogArchive.numUsers,
                "Latest table": latestTableDescription,
                "Size in MB": Math.round((gameLogArchive.sizeBytes) / (1024 * 1024)),
            }
        });
        innerContent = (
        <Table
            cols={["Link", "Date", "Type", "Games", "Users", "Latest table", "Size in MB"]}
            rows={rows}
            key="game-log-archives"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogArchivesTable;
