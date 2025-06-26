import { render, screen } from '@testing-library/react';
import React from 'react';
import { emptyUser } from '../types/User';
import GameStatistics, { emptyGameStatistics } from '../types/GameStatistics';
import {BrowserRouter} from 'react-router-dom'
import TournamentResultsTable from './TournamentResultsTable';
import GameLog, { emptyGameLog } from '../types/GameLog';

it('should handle when no data was retrieved', async () => {
    render(
        <TournamentResultsTable statistics={[]}/>
    );
    expect(await screen.findByText("Error: tournament results could not be retrieved!")).toBeInTheDocument();
});

it('should handle a single win', async () => {
    const stat: GameStatistics = {
        ...emptyGameStatistics,
        user: {
            ...emptyUser,
            id: 1,
            bgaId: 2,
            name: "test-user-1",
        },
        rank: 1,
    }
    render(
        <TournamentResultsTable statistics={[stat]}/>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("test-user-1")).toBeInTheDocument();
});

it('should handle a single loss', async () => {
    const stat: GameStatistics = {
        ...emptyGameStatistics,
        user: {
            ...emptyUser,
            id: 1,
            bgaId: 2,
            name: "test-user-1",
        },
        rank: 2,
    }

    render(
        <TournamentResultsTable statistics={[stat]}/>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("test-user-1")).toBeInTheDocument();
    expect(await screen.findByText("-1")).toBeInTheDocument();
});

it('should handle a pair of results', async () => {
    const stats: GameStatistics[] = [
        {
            ...emptyGameStatistics,
            user: {
                ...emptyUser,
                id: 1,
                bgaId: 2,
                name: "test-user-1",
            },
            rank: 1,
        },
        {
            ...emptyGameStatistics,
            user: {
                ...emptyUser,
                id: 3,
                bgaId: 4,
                name: "test-user-2",
            },
            rank: 2,
        },
    ];

    render(
        <TournamentResultsTable statistics={stats}/>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("test-user-1")).toBeInTheDocument();
    expect(await screen.findByText("test-user-2")).toBeInTheDocument();
    expect(await screen.findByText("-1")).toBeInTheDocument();
});
