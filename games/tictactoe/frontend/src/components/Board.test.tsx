import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import Board from './Board';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <Board xIsNext={false} squares={[]} onPlay={() => {}} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
