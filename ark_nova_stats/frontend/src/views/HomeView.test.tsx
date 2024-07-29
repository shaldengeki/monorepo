import { render, screen } from '@testing-library/react';
import HomeView from './HomeView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import React from 'react';

it('should render', async () => {
    render(
      <MockedProvider mocks={[]}>
        <HomeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Hello World!")).toBeInTheDocument();
});
