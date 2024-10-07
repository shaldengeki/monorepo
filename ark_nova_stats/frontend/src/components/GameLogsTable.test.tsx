import { render, screen } from '@testing-library/react';
import GameLogsTable from './GameLogsTable';
import React from 'react';
import GameLog, { emptyGameLog } from '../types/GameLog';
import { emptyUserRatingChange } from '../types/UserRatingChange';
import User, { emptyUser } from '../types/User';

const gameLog: GameLog = {
    ...emptyGameLog,
    id: 1234,
    bgaTableId: 2345,
    start: 1727705813,
    end: 1727740800,
}

it('should handle when no data was retrieved', async () => {
    render(
        <GameLogsTable gameLogs={[]}/>
    );
    expect(await screen.findByText("Error: game logs could not be retrieved!")).toBeInTheDocument();
});

it('should handle a single game log', async () => {
    render(
        <GameLogsTable gameLogs={[gameLog]}/>
    );
    expect(await screen.findByText("2024-09-30")).toBeInTheDocument();
    expect(await screen.findByText("2024-10-1")).toBeInTheDocument();
    expect(await screen.findByText("1234")).toBeInTheDocument();
    expect(await screen.findByText("2345")).toBeInTheDocument();
});

it('should handle a single game log with rating changes', async () => {
    const gameLogWithRatingChanges: GameLog = {
        ...gameLog,
        gameRatingChanges: [
            {
                ...emptyUserRatingChange,
                priorElo: 1823,
                priorArenaElo: 3846,
            },
        ]
    }

    render(
        <GameLogsTable gameLogs={[gameLogWithRatingChanges]}/>
    );
    expect(await screen.findByText("1823")).toBeInTheDocument();
    expect(await screen.findByText("3846")).toBeInTheDocument();
});

it('should not render arena ELO when it is null', async () => {
    const gameLogWithRatingChanges: GameLog = {
        ...gameLog,
        gameRatingChanges: [
            {
                ...emptyUserRatingChange,
                priorElo: 1823,
                priorArenaElo: null,
            },
        ]
    }

    render(
        <GameLogsTable gameLogs={[gameLogWithRatingChanges]}/>
    );
    expect(await screen.findByText("1823")).toBeInTheDocument();
});

it('should render ELO changes when current player is set', async () => {
    const currentPlayer: User = {
        ...emptyUser,
        bgaId: 6283,
    }
    const gameLogWithRatingChanges: GameLog = {
        ...gameLog,
        gameRatingChanges: [
            {
                ...emptyUserRatingChange,
                user: currentPlayer,
                priorElo: 1823,
                newElo: 3281,
                priorArenaElo: 3846,
                newArenaElo: 6483,
            },
        ]
    }

    render(
        <GameLogsTable gameLogs={[gameLogWithRatingChanges]} currentPlayer={currentPlayer}/>
    );
    expect(await screen.findByText("Normal: 1823 -&gt; 3846")).toBeInTheDocument();
    expect(await screen.findByText("Arena: 3846 -&gt; 6483")).toBeInTheDocument();
});
