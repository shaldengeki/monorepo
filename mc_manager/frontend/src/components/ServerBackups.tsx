import * as React from 'react'
import _ from 'lodash'
import { gql } from '@apollo/client/core';
import { useMutation, useQuery } from '@apollo/client/react';

import { serverBackupStatusSymbol } from '../Utils'
import type Backup from '../types/Backup'
import Table from '../../../../react_library/Table';

const GET_SERVER_BACKUPS = gql`
    query ServerBackups($name: String, $limit: Int) {
        servers(name: $name) {
            id
            latestLog {
                state
            }
            backups(limit: $limit) {
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

type ServerBackupsTableRow = {
    "Created": React.JSX.Element,
    "State": React.JSX.Element,
    "Error?": React.JSX.Element,
    "Restore": React.JSX.Element,

}

type ServerBackupsProps = {
  name?: string
};

const ServerBackupsListing = ({ name }: ServerBackupsProps) => {
  const { data, loading, error } = useQuery(GET_SERVER_BACKUPS, {
    variables: { name, limit: 7 },
    pollInterval: 60_000
  })

  const [enqueueServerBackup, { data: enqueueData, loading: enqueueLoading, error: enqueueError }] = useMutation(ENQUEUE_SERVER_BACKUP)

  const loadingDisplay = <h1>Loading backups...</h1>
  const errorDisplay = <h1>Error loading backups!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const server = data.servers[0]
  const serverLatestStateIsRestoring = (server.latestLog && (server.latestLog.state === 'restore_queued' || server.latestLog.state === 'restore_started'))

  const formattedBackups : Array<ServerBackupsTableRow> = _.map(server.backups || [], (backup) => {
    const createdFormatted = new Date(backup.created * 1000).toLocaleDateString('en-US')
    const restoreLink = (serverId: number, backup: Backup) => {
      if (enqueueLoading) return '🕜Enqueueing restoration...'
      if (enqueueError) return '❌Enqueueing backup failed'

      const restoreEnqueued = enqueueData && enqueueData.backup && enqueueData.backup.id
      if (serverLatestStateIsRestoring || restoreEnqueued) return '✅Restoration enqueued!'
      if (backup.state === 'completed') {
        return (
          <button className="bg-purple-600 hover:bg-purple-700 text-gray-50 px-4 py-3 rounded-full" onClick={e => {
            e.preventDefault()
            enqueueServerBackup({ variables: { serverId, backupId: backup.id } })
          }}>Restore</button>
        )
      } else {
        return (
          <span />
        )
      }
    }

    return {
      "Created": <p>{createdFormatted}</p>,
      "State": <p>{serverBackupStatusSymbol(backup.state)} {backup.state}`</p>,
      "Error?": <p>{backup.error}</p>,
      "Restore": <p>{restoreLink(server.id, backup)}</p>
    }
  })

  return (
        <Table<ServerBackupsTableRow> showFilters={false} rows={formattedBackups} keyName='backups' />
  )
}

const ServerBackups = ({ name }: ServerBackupsProps) => {
  return (
    <div>
      <p className="text-3xl py-4">Backups</p>
      <ServerBackupsListing name={name} />
    </div>
  )
}

export default ServerBackups
