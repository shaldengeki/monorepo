import React from 'react'
import './App.css'
import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom'

import Header from './components/Header'
import ServerListing from './components/ServerListing'

function App () {
  return (
    <Router>
        <Switch>
          <Route path="/">
            <div className="bg-gray-500 w-full h-screen">
              <div className="p-4 content-start">
                <Header />
                <div className="bg-gray-50 rounded overflow-auto">
                  <ServerListing />
                </div>
              </div>
            </div>
          </Route>
        </Switch>
    </Router>
  )
}

export default App
