import React from 'react'
import ReactDOM from 'react-dom'
import App from './App'

import { ApolloClient, HttpLink, InMemoryCache, ApolloProvider } from '@apollo/client';

const cache = new InMemoryCache()

const { REACT_APP_API_PROTOCOL = 'http', REACT_APP_API_HOST = 'localhost', REACT_APP_API_PORT = '5000', REACT_APP_API_PATH = 'graphql' } = process.env

const link = new HttpLink({
  uri: `${REACT_APP_API_PROTOCOL}://${REACT_APP_API_HOST}:${REACT_APP_API_PORT}/${REACT_APP_API_PATH}`
})

const client = new ApolloClient({
  cache,
  link
})

ReactDOM.render(
  <React.StrictMode>
    <ApolloProvider client={client} >
      <App />
    </ApolloProvider>
  </React.StrictMode>,
  document.getElementById('root')
)
