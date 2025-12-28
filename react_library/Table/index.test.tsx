import { test } from 'vitest'
import "@testing-library/jest-dom";
import "@testing-library/jest-dom/vitest";
import { render, screen } from '@testing-library/react';
import Table from './index';

type TestTableRow = {
    "Some": React.JSX.Element,
    "Column": React.JSX.Element,
    "Names": React.JSX.Element,
}

test('should handle when no data was passed', async () => {
    render(<Table<TestTableRow> keyName={'test-key'} rows={[]}/>);
    expect(await screen.findByText("No data to show!")).toBeInTheDocument();
});

// test('should handle a single entry', async () => {
//     const rows: TestTableRow[] = [
//         {"Some": <p>Some1</p>, "Column": <p>Column1</p>, "Names": <p>Name1</p>},
//     ]
//     const { getByText } = await render(
//         <Table<TestTableRow> keyName={'test-key'} rows={rows}/>
//     );
//     await expect.element(getByText("Some1")).toBeInTheDocument();
//     await expect.element(getByText("Column1")).toBeInTheDocument();
//     await expect.element(getByText("Name1")).toBeInTheDocument();
// });

// test('should handle multiple entries', async () => {
//     const rows: TestTableRow[] = [
//         {"Some": <p>Some1</p>, "Column": <p>Column1</p>, "Names": <p>Name1</p>},
//         {"Some": <p>Some2</p>, "Column": <p>Column2</p>, "Names": <p>Name2</p>},
//     ]
//     const { getByText } = await render(
//         <Table<TestTableRow> keyName={'test-key'} rows={rows}/>
//     );
//     await expect.element(getByText("Some2")).toBeInTheDocument();
//     await expect.element(getByText("Column2")).toBeInTheDocument();
//     await expect.element(getByText("Name2")).toBeInTheDocument();
// });
