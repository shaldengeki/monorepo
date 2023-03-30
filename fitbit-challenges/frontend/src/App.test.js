import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import { ApolloProvider } from '@apollo/react-hooks';
import { ApolloClient } from 'apollo-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { HttpLink } from 'apollo-link-http';



it('renders without crashing', () => {
  const cache = new InMemoryCache();
  const link = new HttpLink({
    uri: `http://${process.env.REACT_APP_API_HOST}:${process.env.REACT_APP_API_PORT}/graphql`
  });

  const client = new ApolloClient({
    cache,
    link
  });

  const div = document.createElement('div');
  ReactDOM.render(
    <ApolloProvider client={client} >
        <App />
    </ApolloProvider>, div);
  ReactDOM.unmountComponentAtNode(div);
});
