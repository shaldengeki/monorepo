import { render, screen } from '@testing-library/react';
import App from './App';
import { MockedProvider } from '@apollo/react-testing';

it('should render loading state initially', () => {
  render(
    <MockedProvider mocks={[]}>
      <App />
    </MockedProvider>,
  );
  const linkElement = screen.getByText(/Loading/i);
  expect(linkElement).toBeInTheDocument();
});
