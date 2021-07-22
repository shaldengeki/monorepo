import React from 'react'
import ReactDOM from 'react-dom'
import "tailwindcss/tailwind.css"
import './index.css'
import App from './App'
import reportWebVitals from './reportWebVitals'

import { ApolloProvider } from '@apollo/react-hooks'
import {
  ApolloClient,
  InMemoryCache,
  HttpLink
} from '@apollo/client'

const cache = new InMemoryCache()

const { REACT_APP_API_SCHEME = 'http', REACT_APP_API_HOST = 'localhost', REACT_APP_API_PORT = '5000', REACT_APP_API_PATH = 'graphql' } = process.env

const link = new HttpLink({
  uri: `${REACT_APP_API_SCHEME}://${REACT_APP_API_HOST}:${REACT_APP_API_PORT}/${REACT_APP_API_PATH}`
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

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
