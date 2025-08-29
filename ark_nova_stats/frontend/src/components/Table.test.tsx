import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import React from 'react';
import Table from './Table';

type TestTableRow = {
    "Some": React.JSX.Element,
    "Column": React.JSX.Element,
    "Names": React.JSX.Element,
}

it('should handle when no data was passed', async () => {
    render(
        <Table<TestTableRow> keyName={'test-key'} rows={[]}/>
    );
    expect(await screen.findByText("No data to show!")).toBeInTheDocument();
});

it('should handle a single entry', async () => {
    const rows: TestTableRow[] = [
        {"Some": <p>Some1</p>, "Column": <p>Column1</p>, "Names": <p>Name1</p>},
    ]
    render(
        <Table<TestTableRow> keyName={'test-key'} rows={rows}/>
    );
    expect(await screen.findByText("Some1")).toBeInTheDocument();
    expect(await screen.findByText("Column1")).toBeInTheDocument();
    expect(await screen.findByText("Name1")).toBeInTheDocument();
});

it('should handle multiple entries', async () => {
    const rows: TestTableRow[] = [
        {"Some": <p>Some1</p>, "Column": <p>Column1</p>, "Names": <p>Name1</p>},
        {"Some": <p>Some2</p>, "Column": <p>Column2</p>, "Names": <p>Name2</p>},
    ]
    render(
        <Table<TestTableRow> keyName={'test-key'} rows={rows}/>
    );
    expect(await screen.findByText("Some2")).toBeInTheDocument();
    expect(await screen.findByText("Column2")).toBeInTheDocument();
    expect(await screen.findByText("Name2")).toBeInTheDocument();
});
