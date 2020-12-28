import * as React from 'react'
import _ from 'lodash'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'

import { serverBackupStatusSymbol } from '../Utils'
import Table from './Table'

const GET_SERVER_BACKUPS = gql`
    query ServerBackups($name: String) {
        servers(name: $name) {
            backups {
                id
                created
                state
                error
            }
        }
    }
`

type ServerBackup = {
    created: string,
    state: string,
    error?: string,
  }

type ServerBackupsProps = {
  name?: string
};

const ServerBackups = ({ name }: ServerBackupsProps) => {
  const { data, loading, error } = useQuery(GET_SERVER_BACKUPS, {
    variables: { name },
    pollInterval: 60_000
  })

  const loadingDisplay = <h1>Loading backups...</h1>
  const errorDisplay = <h1>Error loading backups!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const server = data.servers[0]

  const formattedBackups : Array<ServerBackup> = _.map(server.backups || [], (backup) => {
    const createdFormatted = new Date(backup.created * 1000).toLocaleDateString('en-US')

    return {
      created: createdFormatted,
      state: `${serverBackupStatusSymbol(backup.state)} ${backup.state}`,
      error: backup.error
    }
  })

  const cols = [
    'created',
    'state',
    'error'
  ]
  return (
        <Table cols={cols} rows={formattedBackups} key='backups' />
  )
}

export default ServerBackups
