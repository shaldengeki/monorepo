import React from 'react'
import {
  Switch,
  Route,
  useRouteMatch,
  useParams
} from 'react-router-dom'

import ServerHeader from '../components/ServerHeader'
import ServerInfo from '../components/ServerInfo'
import ServerListing from '../components/ServerListing'

function Server () {
  const { serverName } = useParams<{ serverName: string }>()
  return (
    <div>
      <ServerHeader name={serverName} />
      <ServerInfo name={serverName} />
    </div>
  )
}

function Servers () {
  const match = useRouteMatch()

  return (
        <div className="bg-gray-50 rounded overflow-auto">
            <Switch>
                <Route path={`${match.path}/:serverName`}>
                    <Server />
                </Route>
                <Route path={match.path}>
                    <ServerListing />
                </Route>
            </Switch>
        </div>
  )
}

export default Servers
