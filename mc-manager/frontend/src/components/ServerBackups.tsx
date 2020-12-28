import * as React from 'react'
import _ from 'lodash'
import { useQuery, useMutation } from '@apollo/react-hooks'
import gql from 'graphql-tag'

import { serverBackupStatusSymbol } from '../Utils'
import Table from './Table'

const GET_SERVER_BACKUPS = gql`
    query ServerBackups($name: String) {
        servers(name: $name) {
            id
            backups {
                id
                created
                state
                error
            }
        }
    }
`

const ENQUEUE_SERVER_BACKUP = gql`
    mutation EnqueueServerBackup($serverId:Int!, $backupId:Int!) {
        createServerLog(
            serverId:$serverId,
            state:restore_queued,
            backupId:$backupId
        ) {
            state
            backup {
                id
            }
        }
    }
`

type ServerBackup = {
    created: string,
    state: string,
    error?: string,
    restore: any
  }

type ServerBackupsProps = {
  name?: string
};

const ServerBackups = ({ name }: ServerBackupsProps) => {
  const { data, loading, error } = useQuery(GET_SERVER_BACKUPS, {
    variables: { name },
    pollInterval: 60_000
  })

  const [enqueueServerBackup, { data: enqueueData, loading: enqueueLoading, error: enqueueError }] = useMutation(ENQUEUE_SERVER_BACKUP)

  const loadingDisplay = <h1>Loading backups...</h1>
  const errorDisplay = <h1>Error loading backups!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const server = data.servers[0]

  const formattedBackups : Array<ServerBackup> = _.map(server.backups || [], (backup) => {
    const createdFormatted = new Date(backup.created * 1000).toLocaleDateString('en-US')
    const restoreLink = (serverId: number, backupId: number) => {
      if (enqueueLoading) return '🕜Enqueueing restoration...'
      if (enqueueError) return '❌Enqueueing backup failed'
      if (enqueueData && enqueueData.backup && enqueueData.backup.id) return '✅Restoration enqueued!'
      return (
            <a onClick={e => {
              e.preventDefault()
              enqueueServerBackup({ variables: { serverId, backupId } })
            }}>Restore</a>
      )
    }

    return {
      created: createdFormatted,
      state: `${serverBackupStatusSymbol(backup.state)} ${backup.state}`,
      error: backup.error,
      restore: restoreLink(server.id, backup.id)
    }
  })

  const cols = [
    'created',
    'state',
    'error',
    'restore'
  ]
  return (
        <Table cols={cols} rows={formattedBackups} key='backups' />
  )
}

export default ServerBackups
