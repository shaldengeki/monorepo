import React from 'react';

import GameLog from '../types/GameLog';
import User from '../types/User';
import Table from '../../../../react_library/Table';
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
    if (!gameLogs) {
        return <p>Error: game logs could not be retrieved!</p>;
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
                    const priorElos = [];
                    const linkTextParts = [user.name];
                    if (ratingChange?.priorElo) {
                        priorElos.push(ratingChange.priorElo)
                        if (ratingChange.priorArenaElo) {
                            priorElos.push(ratingChange.priorArenaElo);
                        }

                        linkTextParts.push("(" + priorElos.join(" / ") + ")");
                    }

                    return <li>
                        <PageLink to={`/user/${user.name}`}>
                            {linkTextParts.join(" ")}
                        </PageLink>
                    </li>;
                })}</ul>,
            }
            if (currentPlayer !== undefined) {
                const ratingChange = gameLog.gameRatingChanges.find((change) => { return change.user.bgaId === currentPlayer.bgaId })
                if (ratingChange) {
                    const ratingChanges = [`Normal: ${ratingChange.priorElo} -> ${ratingChange.newElo}`];
                    if (ratingChange.priorArenaElo) {
                        ratingChanges.push(`Arena: ${ratingChange.priorArenaElo} -> ${ratingChange.newArenaElo}`)
                    }
                    rowAttrs["Rating changes"] = <ul>
                        {ratingChanges.map((change) => { return <li>{change}</li>})}
                    </ul>;
                }
            }

            return rowAttrs;
        });
        return <Table<GameLogsTableRow>
            rows={rows}
            keyName="game-logs"
            showFilters={false}
        />;
    }
}

export default GameLogsTable;
