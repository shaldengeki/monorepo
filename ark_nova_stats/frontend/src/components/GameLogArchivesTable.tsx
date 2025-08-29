import React from 'react';

import {getDate} from '../../../../react_library/DateUtils';
import GameLogArchive from '../types/GameLogArchive';
import Table from './Table';
import PageLink from './PageLink';

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
    if (!gameLogArchives) {
        return <p>Error: game log archives could not be retrieved!</p>;
    } else {
        const rows: GameLogArchivesTableRow[] = gameLogArchives.map((gameLogArchive: GameLogArchive) => {
            let latestTableDescription = <PageLink to={"https://boardgamearena.com/table?table=" + gameLogArchive.maxGameLog.bgaTableId}>
                {gameLogArchive.maxGameLog.bgaTableId}
            </PageLink>;
            return {
                "Link": <PageLink to={gameLogArchive.url}>Download</PageLink>,
                "Date": <p>{getDate(gameLogArchive.createdAt)}</p>,
                "Type": <p>{gameLogArchive.archiveType}</p>,
                "Games": <p>{gameLogArchive.numGameLogs}</p>,
                "Users": <p>{gameLogArchive.numUsers}</p>,
                "Latest table": <p>{latestTableDescription}</p>,
                "Size in MB": <p>{Math.round((gameLogArchive.sizeBytes) / (1024 * 1024))}</p>,
            }
        });
        return (
        <Table<GameLogArchivesTableRow>
            rows={rows}
            keyName="game-log-archives"
            showFilters={false}
        />
       );
    }
}

export default GameLogArchivesTable;
