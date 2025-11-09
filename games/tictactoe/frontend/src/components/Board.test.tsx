import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import Board from './Board';
import { MockedProvider } from '@apollo/client/testing/react';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <Board xIsNext={false} squares={[]} onPlay={() => {}} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Next player: O")).toBeInTheDocument();
});
