import { render, screen } from '@testing-library/react';
import CardsView, { CARDS_VIEW_QUERY } from './CardsView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'

it('should render the name of the view', async () => {
  const testFetchCardsMock = {
    request: {
      query: CARDS_VIEW_QUERY
    },
    result: {
      data: {
        cards: [],
      }
    }
  }

  render(
      <MockedProvider mocks={[testFetchCardsMock]}>
        <CardsView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
  );
  expect(await screen.findByText("Cards")).toBeInTheDocument();
});


it('should render cards when provided', async () => {
    const testFetchCardsMock = {
      request: {
        query: CARDS_VIEW_QUERY
      },
      result: {
        data: {
          cards: [
            { bgaId: "testCard", name: "test card", mostPlayedBy: [{user: {name: "test user"}, count: 100}]}
          ],
        }
      }
    }

    render(
        <MockedProvider mocks={[testFetchCardsMock]}>
          <CardsView />
        </MockedProvider>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("test card")).toBeInTheDocument();
  });



it('should render most-commonly played user when provided', async () => {
    const testFetchCardsMock = {
      request: {
        query: CARDS_VIEW_QUERY
      },
      result: {
        data: {
          cards: [
            { bgaId: "testCard", name: "test card", mostPlayedBy: [{user: {name: "test user"}, count: 100}]}
          ],
        }
      }
    }

    render(
        <MockedProvider mocks={[testFetchCardsMock]}>
          <CardsView />
        </MockedProvider>,
        {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("test user (100)")).toBeInTheDocument();
  });
