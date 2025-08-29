import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import DatabaseStatistics from './DatabaseStatistics';
import React from 'react';
import { emptyStats, exampleStats } from '../types/Stats';

it('should handle when no data was retrieved', async () => {
    render(
        <DatabaseStatistics stats={undefined}/>
    );
    expect(await screen.findByText("Error: stats could not be retrieved!")).toBeInTheDocument();
});

it('should handle when no game logs are present', async () => {
    render(
        <DatabaseStatistics stats={emptyStats}/>
    );
    expect(await screen.findByText("Games recorded: 0")).toBeInTheDocument();
    expect(await screen.findByText("Players involved: 0")).toBeInTheDocument();
});


it('should handle when game logs are present', async () => {
    render(
        <DatabaseStatistics stats={exampleStats} />
    );
    expect(await screen.findByText("Games recorded: 52")).toBeInTheDocument();
    expect(await screen.findByText("Players involved: 19")).toBeInTheDocument();
    expect(await screen.findByText("The most recent game was submitted on: 2044-06-05")).toBeInTheDocument();
});
