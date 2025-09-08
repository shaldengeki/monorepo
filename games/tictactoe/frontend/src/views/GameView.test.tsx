import { render, screen } from '@testing-library/react';
import GameView from './GameView';
import { MockedProvider } from '@apollo/client/testing';
import {BrowserRouter} from 'react-router-dom'


test('should render', async () => {
    render(
      <MockedProvider mocks={[]}>
        <GameView logo={"test"} />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Tic-Tac-Toe")).toBeInTheDocument();
});
