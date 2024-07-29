import { render, screen } from '@testing-library/react';
import HomeView from './HomeView';
import { FETCH_STATS_QUERY } from './HomeView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import React from 'react';
import { emptyStats, exampleStats } from '../types/Stats';

it('should handle when no data was retrieved', async () => {
  const testFetchStatsMock = {
    request: {
      query: FETCH_STATS_QUERY
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
  expect(await screen.findByText("Error: stats could not be retrieved!")).toBeInTheDocument();
});

it('should handle when no game logs are present', async () => {
  const testFetchStatsMock = {
    request: {
      query: FETCH_STATS_QUERY
    },
    result: {
      data: {
        stats: emptyStats
      }
    }
  }

  render(
      <MockedProvider mocks={[testFetchStatsMock]}>
        <HomeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("Games recorded: 0")).toBeInTheDocument();
  expect(await screen.findByText("Players involved: 0")).toBeInTheDocument();
});


it('should handle when game logs are present', async () => {
  const testFetchStatsMock = {
    request: {
      query: FETCH_STATS_QUERY
    },
    result: {
      data: {
        stats: exampleStats
      }
    }
  }

  render(
      <MockedProvider mocks={[testFetchStatsMock]}>
        <HomeView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("Games recorded: 52")).toBeInTheDocument();
  expect(await screen.findByText("Players involved: 19")).toBeInTheDocument();
  expect(await screen.findByText("The most recent game was submitted on: 2044-06-05")).toBeInTheDocument();
});
