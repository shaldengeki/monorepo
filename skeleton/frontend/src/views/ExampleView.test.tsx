import { render, screen } from '@testing-library/react';
import ExampleView from './ExampleView';
import { MockedProvider } from '@apollo/client/testing/react';
import {BrowserRouter} from 'react-router-dom'


test('should render', async () => {
    render(
      <MockedProvider mocks={[]}>
        <ExampleView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Page Container")).toBeInTheDocument();
});
