import * as React from 'react'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'

import { timeAgo, serverLogStatusSymbol, serverBackupStatusSymbol } from '../Utils'

const { REACT_APP_API_HOST = 'localhost' } = process.env

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
  return `${serverBackupStatusSymbol(state)} ${state}, ${timeAgo(created)}`
}

type LogProps = {
  created: number,
  state: string,
  error?: string,
  backup: BackupProps
}

const displayLog = ({ created, state, error, backup }: LogProps): string => {
  return `${serverLogStatusSymbol(state)} ${state} ${timeAgo(created)}`
}

const displayServerUrl = (port: number): string => {
  return `${REACT_APP_API_HOST}:${port}`
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
    <table className="table-auto border-collapse border">
      <tbody>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">Mod</td>
          <td className="border border-gray-300 px-4 py-2">{server.zipfile}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">Latest status</td>
          <td className="border border-gray-300 px-4 py-2">{displayLog(server.latestLog)}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">URL</td>
          <td className="border border-gray-300 px-4 py-2">{displayServerUrl(server.port)}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">Created</td>
          <td className="border border-gray-300 px-4 py-2">{timeAgo(server.created)}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">Creator</td>
          <td className="border border-gray-300 px-4 py-2">{server.createdBy}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">MOTD</td>
          <td className="border border-gray-300 px-4 py-2">{server.motd}</td>
        </tr>
        <tr>
          <td className="font-medium border border-gray-300 px-4 py-2">Latest backup</td>
          <td className="border border-gray-300 px-4 py-2">{displayBackup(server.latestBackup)}</td>
        </tr>
      </tbody>
    </table>
  )
}

export default ServerInfo
