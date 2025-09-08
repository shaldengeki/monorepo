import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import ExampleComponent from './ExampleComponent';
import { MockedProvider } from '@apollo/client/testing';

it('should render', async () => {
    render(
        <MockedProvider mocks={[]}>
            <ExampleComponent />
        </MockedProvider>,
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
