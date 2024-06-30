import { render, screen } from '@testing-library/react';
import ExampleView from './ExampleView';
import { EXAMPLE_QUERY } from './ExampleView';
import { MockedProvider } from '@apollo/react-testing';
import {BrowserRouter} from 'react-router-dom'
import React from 'react';

it('should render', async () => {
    const testQueryMock =   {
      request: {
        query: EXAMPLE_QUERY,
        variables: {
            id: 0
        },
      },
      result: {
        data: {
          foo: {
            id: 1,
          },
        }
      }
    };
    render(
      <MockedProvider mocks={[testQueryMock]}>
        <ExampleView />
      </MockedProvider>,
      {wrapper: BrowserRouter},
    );
    expect(await screen.findByText("Example component")).toBeInTheDocument();
});
