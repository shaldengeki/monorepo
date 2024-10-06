import { render, screen } from '@testing-library/react';
import EmuCupView, { EMU_CUP_VIEW_QUERY } from './EmuCupView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import React from 'react';
import { emptyGameLog } from '../types/GameLog';
import EmuCupTableIds from '../EmuCupTableIds';

it('should render the name of the view', async () => {
  const testEmuCupQueryMock = {
    request: {
      query: EMU_CUP_VIEW_QUERY,
      variables: {tableIds: EmuCupTableIds},
    },
    result: {
      data: {
        gameStatistics: null,
        gameRatings: null,
      }
    }
  }

  render(
      <MockedProvider mocks={[testEmuCupQueryMock]}>
        <EmuCupView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("Emu Cup")).toBeInTheDocument();
});


it('should render with no game statistics present', async () => {
    const testEmuCupQueryMock = {
      request: {
        query: EMU_CUP_VIEW_QUERY,
        variables: {tableIds: EmuCupTableIds},
    },
      result: {
        data: {
            gameStatistics: [],
        }
      }
    }

    render(
        <MockedProvider mocks={[testEmuCupQueryMock]}>
          <EmuCupView />
        </MockedProvider>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("No games found!")).toBeInTheDocument();
});
