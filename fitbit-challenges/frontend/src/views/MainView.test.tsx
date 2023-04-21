import { render, screen } from '@testing-library/react';
import MainView, { TEST_QUERY } from './MainView';
import { MockedProvider } from '@apollo/react-testing';
import React from 'react';

it('should render loading state initially', async () => {
  const testQueryMock =   {
    request: {
      query: TEST_QUERY,
    },
    result: {
      data: {
        test: "hello world!"
      }
    }
  };
  render(
    <MockedProvider mocks={[testQueryMock]}>
      <MainView />
    </MockedProvider>,
  );
  expect(await screen.findByText("Loading...")).toBeInTheDocument();
  expect(await screen.findByText("hello world!")).toBeInTheDocument();
});
