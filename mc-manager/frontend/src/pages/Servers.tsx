import React from 'react'
import {
  Switch,
  Route,
  useRouteMatch,
  useParams
} from 'react-router-dom'

import ServerBackups from '../components/ServerBackups'
import ServerHeader from '../components/ServerHeader'
import ServerInfo from '../components/ServerInfo'
import ServerListing from '../components/ServerListing'
// import ServerLogs from '../components/ServerLogs'

function Server () {
  const { name } = useParams<{ name: string }>()
  return (
    <div>
      <ServerHeader name={name} />
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1"><ServerInfo name={name} /></div>
        <div className="col-span-2"><ServerBackups name={name} /></div>
        {/* <div className="col-span-3"><ServerLogs name={name} /></div> */}
      </div>
    </div>
  )
}

function Servers () {
  const match = useRouteMatch()

  return (
        <div className="bg-gray-50 rounded overflow-auto p-4">
            <Switch>
                <Route path={`${match.path}/:name`}>
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
