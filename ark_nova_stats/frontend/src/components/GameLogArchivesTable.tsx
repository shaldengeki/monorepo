import React from 'react';
import { Link } from 'react-router-dom';

import {getDate} from '../DateUtils';
import GameLogArchive from '../types/GameLogArchive';
import Table from './Table';
import { round } from 'lodash';

type GameLogArchivesTableParams = {
    gameLogArchives: GameLogArchive[];
}

const GameLogArchivesTable = ({gameLogArchives}: GameLogArchivesTableParams) => {
    let innerContent = <p></p>;
    if (!gameLogArchives) {
        innerContent = <p>Error: game log archives could not be retrieved!</p>;
    } else {
        var rows = gameLogArchives.map((gameLogArchive: GameLogArchive) => {
            let latestTablePlayers = gameLogArchive.maxGameLog.users.join(', ');
            let latestTableDescription = `${gameLogArchive.maxGameLog.bgaTableId}, between ${latestTablePlayers}`;
            return {
                "Date": getDate(gameLogArchive.createdAt),
                "Type": gameLogArchive.archiveType,
                "Games": gameLogArchive.numGameLogs,
                "Users": gameLogArchive.numUsers,
                "Latest table": latestTableDescription,
                "Size (MB)": round((gameLogArchive.sizeBytes) / (1024 * 1024), 0),
                "Link": <Link to={gameLogArchive.url}>Download</Link>,
            }
        });
        innerContent = (
        <Table
            cols={["Date", "Type", "Games", "Users", "Latest table", "Size (MB)", "Link"]}
            rows={rows}
            key="game-log-archives"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogArchivesTable;
