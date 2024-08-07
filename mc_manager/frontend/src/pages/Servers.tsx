import {
  Routes,
  Route,
  useLocation,
  useParams
} from 'react-router-dom'

import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';

import ServerBackups from '../components/ServerBackups'
import ServerHeader from '../components/ServerHeader'
import ServerInfo from '../components/ServerInfo'
import ServerControls from '../components/ServerControls'
import ServerListing from '../components/ServerListing'
// import ServerLogs from '../components/ServerLogs'

const GET_SERVER_INFO = gql`
    query ServerInfo($name: String) {
        servers(name: $name) {
            id
            name
            created
            createdBy
            memory
            motd
            port
            zipfile
            latestLog {
                created
                state
                error
                backup {
                  created
                  state
                  error
                  remotePath
                }
            }
            latestBackup {
                created
                state
                error
                remotePath
            }
        }
    }
`

function Server () {
  const { name } = useParams<{ name: string }>()

  const { data, loading, error } = useQuery(GET_SERVER_INFO, {
    variables: { name },
    pollInterval: 60_000
  })

  const loadingDisplay = <h1>Loading server...</h1>
  const errorDisplay = <h1>Error loading server!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const server = data.servers[0]

  return (
    <div>
      <ServerHeader name={server.name} />
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1">
          <ServerInfo server={server} />
          <ServerControls server={server} />
        </div>
        <div className="col-span-2"><ServerBackups name={name} /></div>
        {/* <div className="col-span-3"><ServerLogs name={name} /></div> */}
      </div>
    </div>
  )
}

function Servers () {
  const { pathname } = useLocation()

  return (
        <div className="bg-gray-50 rounded overflow-auto p-4">
            <Routes>
                <Route path={`${pathname}/:name`} element={<Server />} />
                <Route path={pathname} element={<ServerListing />} />
            </Routes>
        </div>
  )
}

export default Servers
