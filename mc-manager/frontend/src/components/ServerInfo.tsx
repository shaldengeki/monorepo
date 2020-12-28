import * as React from 'react'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'

import { timeAgo } from '../Utils'

const GET_SERVER_INFO = gql`
    query GetServerInfo($name: String) {
        servers(name: $name) {
            id
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

type BackupProps = {
  created: number,
  state: string,
  error?: string,
  remotePath?: string
}

const displayBackup = ({ created, state, error, remotePath }: BackupProps): string => {
  return `${state} at ${timeAgo(created)}`
}

type LogProps = {
  created: number,
  state: string,
  error?: string,
  backup: BackupProps
}

const displayLog = ({ created, state, error, backup }: LogProps): string => {
  return `${state} at ${timeAgo(created)}`
}

type ServerInfoProps = {name: string};

const ServerInfo = ({ name }: ServerInfoProps) => {
  const { data, loading, error } = useQuery(GET_SERVER_INFO, {
    variables: { name },
    pollInterval: 10_000
  })

  const loadingDisplay = <h1>Loading server...</h1>
  const errorDisplay = <h1>Error loading server!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const server = data.servers[0]

  return (
    <table className="table-auto">
      <tbody>
        <tr>
          <td className="font-medium">ID</td>
          <td>{server.id}</td>
        </tr>
        <tr>
          <td className="font-medium">Created</td>
          <td>{timeAgo(server.created)}</td>
        </tr>
        <tr>
          <td className="font-medium">Creator</td>
          <td>{server.createdBy}</td>
        </tr>
        <tr>
          <td className="font-medium">Memory</td>
          <td>{server.memory}</td>
        </tr>
        <tr>
          <td className="font-medium">MOTD</td>
          <td>{server.motd}</td>
        </tr>
        <tr>
          <td className="font-medium">Port</td>
          <td>{server.port}</td>
        </tr>
        <tr>
          <td className="font-medium">Mod</td>
          <td>{server.zipfile}</td>
        </tr>
        <tr>
          <td className="font-medium">Latest status</td>
          <td>{displayLog(server.latestLog)}</td>
        </tr>
        <tr>
          <td className="font-medium">Latest backup</td>
          <td>{displayBackup(server.latestBackup)}</td>
        </tr>
      </tbody>
    </table>
  )
}

export default ServerInfo
