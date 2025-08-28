import { render, screen } from '@testing-library/react';
import HomeView from './HomeView';
import { HOME_VIEW_QUERY } from './HomeView';
import { MockedProvider } from "@apollo/client/testing/react";
import {BrowserRouter} from 'react-router-dom'
import React from 'react';

it('should render the name of the view', async () => {
  const testFetchStatsMock = {
    request: {
      query: HOME_VIEW_QUERY
    },
    result: {
      data: {
        stats: null
      }
    }
  }

  render(
      <MockedProvider mocks={[testFetchStatsMock]}>
        <HomeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("Home")).toBeInTheDocument();
});
