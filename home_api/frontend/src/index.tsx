import {createRoot} from 'react-dom/client';
import './App.css';
import App from './App';
import * as serviceWorker from './serviceWorker';

import { ApolloClient, InMemoryCache} from '@apollo/client';
import { ApolloProvider } from '@apollo/client/react';
import { HttpLink } from '@apollo/client/link/http';
const cache = new InMemoryCache();
const link = new HttpLink({
  uri: `http://${process.env.REACT_APP_API_HOST}:${process.env.REACT_APP_API_PORT}/graphql`
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

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
