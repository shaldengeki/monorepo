import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import './App.css';
import App from './App.tsx';

import { ApolloClient, HttpLink, InMemoryCache, ApolloProvider } from '@apollo/client';

const cache = new InMemoryCache();
const link = new HttpLink({
  uri: `${process.env.REACT_APP_API_PROTOCOL}://${process.env.REACT_APP_API_HOST}:${process.env.REACT_APP_API_PORT}/graphql`
});

const client = new ApolloClient({
  cache,
  link
});

ReactDOM.render(
    <ApolloProvider client={client} >
        <App />
    </ApolloProvider>, document.getElementById('root'));
