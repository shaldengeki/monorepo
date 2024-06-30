import { render, screen } from '@testing-library/react';
import ExampleComponent from './ExampleComponent';
import React from 'react';

it('should render', async () => {
    render(
        <ExampleComponent />,
    );
    expect(await screen.findByText("Example component")).toBeInTheDocument();
});
