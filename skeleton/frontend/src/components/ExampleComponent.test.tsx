import { render, screen } from '@testing-library/react';
import ExampleComponent from './ExampleComponent';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <ExampleComponent />
        </MockedProvider>,
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
