// TODO: figure out how to remove these.
// These should be brought in via vitest.setup.ts, but are not.
import "@testing-library/jest-dom";
import "@testing-library/jest-dom/vitest";

import DatabaseStatistics from './DatabaseStatistics';
import { emptyStats, exampleStats } from '../types/Stats';

import { test } from 'vitest'
import { render, screen } from '@testing-library/react';

test('should handle when no data was retrieved', async () => {
    render(
        <DatabaseStatistics stats={undefined}/>
    );
    expect(await screen.findByText("Error: stats could not be retrieved!")).toBeInTheDocument();
});

test('should handle when no game logs are present', async () => {
    render(
        <DatabaseStatistics stats={emptyStats}/>
    );
    expect(await screen.findByText("Games recorded: 0")).toBeInTheDocument();
    expect(await screen.findByText("Players involved: 0")).toBeInTheDocument();
});


test('should handle when game logs are present', async () => {
    render(
        <DatabaseStatistics stats={exampleStats} />
    );
    expect(await screen.findByText("Games recorded: 52")).toBeInTheDocument();
    expect(await screen.findByText("Players involved: 19")).toBeInTheDocument();
    expect(await screen.findByText("The most recent game was submitted on: 2044-06-05")).toBeInTheDocument();
});
