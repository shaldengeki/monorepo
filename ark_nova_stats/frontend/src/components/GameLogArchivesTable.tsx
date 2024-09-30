import React from 'react';
import { Link } from 'react-router-dom';

import {getDate} from '../DateUtils';
import GameLogArchive from '../types/GameLogArchive';
import Table from './Table';

type GameLogArchivesTableParams = {
    gameLogArchives: GameLogArchive[];
}

type GameLogArchivesTableRow = {
    "Link": React.JSX.Element,
    "Date": React.JSX.Element,
    "Type": React.JSX.Element,
    "Games": React.JSX.Element,
    "Users": React.JSX.Element,
    "Latest table": React.JSX.Element,
    "Size in MB": React.JSX.Element,

}

const GameLogArchivesTable = ({gameLogArchives}: GameLogArchivesTableParams) => {
    let innerContent = <p></p>;
    if (!gameLogArchives) {
        innerContent = <p>Error: game log archives could not be retrieved!</p>;
    } else {
        var rows: GameLogArchivesTableRow[] = gameLogArchives.map((gameLogArchive: GameLogArchive) => {
            let latestTableDescription = <Link to={"https://boardgamearena.com/table?table=" + gameLogArchive.maxGameLog.bgaTableId}>
                {gameLogArchive.maxGameLog.bgaTableId}
            </Link>;
            return {
                "Link": <Link to={gameLogArchive.url}>Download</Link>,
                "Date": <p>{getDate(gameLogArchive.createdAt)}</p>,
                "Type": <p>{gameLogArchive.archiveType}</p>,
                "Games": <p>{gameLogArchive.numGameLogs}</p>,
                "Users": <p>{gameLogArchive.numUsers}</p>,
                "Latest table": <p>{latestTableDescription}</p>,
                "Size in MB": <p>{Math.round((gameLogArchive.sizeBytes) / (1024 * 1024))}</p>,
            }
        });
        innerContent = (
        <Table<GameLogArchivesTableRow>
            rows={rows}
            key="game-log-archives"
            showFilters={false}
        />
       );
    }
    return innerContent
}

export default GameLogArchivesTable;
