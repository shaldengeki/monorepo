import { render, screen } from '@testing-library/react';
import ExampleView from './ExampleView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import React from 'react';

it('should render', async () => {
    render(
      <MockedProvider mocks={[]}>
        <ExampleView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
