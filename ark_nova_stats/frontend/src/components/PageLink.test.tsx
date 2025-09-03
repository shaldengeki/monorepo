import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react';
import PageLink from './PageLink';
import { BrowserRouter } from 'react-router-dom';


it('should render contents when provided text', async () => {
    render(
        <PageLink to={"foo"}>This is my link text!</PageLink>,
        {wrapper: BrowserRouter}
    );
    expect(await screen.findByText("This is my link text!")).toBeInTheDocument();
});

it('should render contents when provided an element', async () => {
    render(
        <PageLink to={"foo"}><div>This is my link text within an element!</div></PageLink>,
        {wrapper: BrowserRouter}
    );
    expect(await screen.findByText("This is my link text within an element!")).toBeInTheDocument();
});
