import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import FormButton from "./FormButton";

it('renders the text provided', async () => {
  render(
    <FormButton>
      Sample placeholder text
    </FormButton>
  );
  expect(await screen.findByText("Sample placeholder text")).toBeInTheDocument();
});

it('handles no hook passed on click', async() => {
  render(<FormButton />);
  const button = screen.getByRole("button");
  fireEvent.click(button);
});

it('calls a provided hook on click', async () => {
  const testHook = jest.fn();
  render(<FormButton hook={testHook} />);
  const button = screen.getByRole("button");
  expect(testHook).toHaveBeenCalledTimes(0);
  fireEvent.click(button);
  expect(testHook).toHaveBeenCalled();
});
