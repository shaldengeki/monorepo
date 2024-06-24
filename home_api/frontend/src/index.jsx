import React from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import App from './App';
import * as serviceWorker from './serviceWorker';

import { ApolloClient, HttpLink, InMemoryCache, ApolloProvider } from '@apollo/client';

const cache = new InMemoryCache();
const link = new HttpLink({
  uri: `http://${process.env.REACT_APP_API_HOST}:${process.env.REACT_APP_API_PORT}/graphql`
});

const client = new ApolloClient({
  cache,
  link
});

ReactDOM.render(
    <ApolloProvider client={client} >
        <App />
    </ApolloProvider>, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
