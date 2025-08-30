import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import Square from './Square';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <Square value={"Hello World!"} onSquareClick={() => {}} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
