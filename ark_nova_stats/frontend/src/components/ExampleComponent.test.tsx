import { render, screen } from '@testing-library/react';
import ExampleComponent from './ExampleComponent';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <ExampleComponent>
                <p>Test render!</p>
            </ExampleComponent>
        </MockedProvider>,
    );
    expect(await screen.findByText("Test render!")).toBeInTheDocument();
});
