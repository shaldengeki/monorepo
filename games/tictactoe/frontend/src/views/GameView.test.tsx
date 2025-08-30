import { render, screen } from '@testing-library/react';
import GameView from './GameView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import * as React from 'react';


test('should render', async () => {
    render(
      <MockedProvider mocks={[]}>
        <GameView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Page Container")).toBeInTheDocument();
});
