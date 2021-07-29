import * as React from 'react'
import { useMutation } from '@apollo/react-hooks'
import gql from 'graphql-tag'

import type Server from '../types/Server'

const ENQUEUE_SERVER_STOP = gql`
    mutation EnqueueServerStop($serverId:Int!) {
        createServerLog(
            serverId:$serverId,
            state:stop_queued,
        ) {
            state
        }
    }
`

type ServerControlsProps = {
  server?: Server
};

const ServerControls = ({ server }: ServerControlsProps) => {
  const [enqueueServerStop, { data: enqueueData, loading: enqueueLoading, error: enqueueError }] = useMutation(ENQUEUE_SERVER_STOP)

  const errorDisplay = <h1>Error loading server info!</h1>

  if (!server) return errorDisplay

  if (enqueueLoading) return (<p>🕜Enqueueing stop...</p>)
  if (enqueueError) return (<p>❌Enqueueing stop failed</p>)

  const serverLatestStateIsStopping = (server.latestLog && (server.latestLog.state === 'stop_queued' || server.latestLog.state === 'stop_started'))
  const serverId = server.id

  const stopButton = (
    <button className="bg-red-600 hover:bg-red-700 text-gray-50 px-4 py-3 rounded-full" onClick={e => {
      e.preventDefault()
      enqueueServerStop({ variables: { serverId } })
    }}>Stop</button>
  )

  const stopEnqueued = enqueueData && enqueueData.backup && enqueueData.backup.id
  if (serverLatestStateIsStopping || stopEnqueued) return (<p>✅Stop enqueued!</p>)
  if (server.latestLog && server.latestLog.state === 'stopped') return (null)
  return stopButton
}

export default ServerControls
