import { render, screen } from '@testing-library/react';
import GameLogArchivesTable from './GameLogArchivesTable';
import { emptyGameLog } from '../types/GameLog';
import GameLogArchive from '../types/GameLogArchive';
import { BrowserRouter } from 'react-router-dom';

const archive: GameLogArchive = {
    id: 12345,
    archiveType: "FAKE_ARCHIVE_TYPE",
    url: "https://fake/url",
    sizeBytes: 3*1024*1024,
    numGameLogs: 1000,
    numUsers: 345,
    maxGameLog: emptyGameLog,
    createdAt: 1727705813,
}

it('should handle when no data was retrieved', async () => {
    render(
        <GameLogArchivesTable gameLogArchives={[]}/>,
        {wrapper: BrowserRouter}
    );
    expect(await screen.findByText("No data to show!")).toBeInTheDocument();
});

it('should handle a single game log archive', async () => {
    render(
        <GameLogArchivesTable gameLogArchives={[archive]}/>,
        {wrapper: BrowserRouter}
    );
    expect(await screen.findByText("2024-09-30")).toBeInTheDocument();
    expect(await screen.findByText("FAKE_ARCHIVE_TYPE")).toBeInTheDocument();
    expect(await screen.findByText("3")).toBeInTheDocument();
    expect(await screen.findByText("1000")).toBeInTheDocument();
    expect(await screen.findByText("345")).toBeInTheDocument();
});
