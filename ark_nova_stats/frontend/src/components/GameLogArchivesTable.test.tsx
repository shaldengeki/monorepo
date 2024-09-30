import { render, screen } from '@testing-library/react';
import GameLogArchivesTable from './GameLogArchivesTable';
import React from 'react';
import { emptyGameLog } from '../types/GameLog';
import GameLogArchive from '../types/GameLogArchive';

const archive: GameLogArchive = {
    id: 12345,
    archiveType: "FAKE_ARCHIVE_TYPE",
    url: "https://fake/url",
    sizeBytes: 234,
    numGameLogs: 1000,
    numUsers: 345,
    maxGameLog: emptyGameLog,
    createdAt: 1727705813,
}

it('should handle when no data was retrieved', async () => {
    render(
        <GameLogArchivesTable gameLogArchives={[]}/>
    );
    expect(await screen.findByText("Error: game log archives could not be retrieved!")).toBeInTheDocument();
});

it('should handle a single game log archive', async () => {
    render(
        <GameLogArchivesTable gameLogArchives={[archive]}/>
    );
    expect(await screen.findByText("2024-09-30")).toBeInTheDocument();
    expect(await screen.findByText("FAKE_ARCHIVE_TYPE")).toBeInTheDocument();
    expect(await screen.findByText("234")).toBeInTheDocument();
    expect(await screen.findByText("1000")).toBeInTheDocument();
    expect(await screen.findByText("345")).toBeInTheDocument();
});
