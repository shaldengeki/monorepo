import {createRoot} from 'react-dom/client';
import './App.css';
import App from './App';

import { ApolloClient, InMemoryCache} from '@apollo/client';
import { ApolloProvider } from '@apollo/client/react';
import { HttpLink } from '@apollo/client/link/http';
const cache = new InMemoryCache();
const link = new HttpLink({
    uri: `${process.env.REACT_APP_API_PROTOCOL}://${process.env.REACT_APP_API_HOST}:${process.env.REACT_APP_API_PORT}/graphql`,
    credentials: 'include',
});

const client = new ApolloClient({
    cache,
    link
});

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(
    <ApolloProvider client={client} >
        <App />
    </ApolloProvider>
)
