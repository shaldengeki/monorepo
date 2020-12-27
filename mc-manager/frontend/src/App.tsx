import React from 'react'
import './App.css'
import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom'

import Header from './components/Header'

import Servers from './pages/Servers'

function App () {
  return (
    <div className="bg-gray-500 w-full h-screen">
      <div className="p-4 content-start">
        <Header />
          <Router>
            <Switch>
              <Route path="/servers">
                <Servers />
              </Route>
              <Route path="/">
                <Servers />
              </Route>
            </Switch>
        </Router>
      </div>
    </div>
  )
}

export default App
