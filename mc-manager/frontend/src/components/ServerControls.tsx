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

const ENQUEUE_SERVER_START = gql`
    mutation EnqueueServerStart($serverId:Int!) {
        createServerLog(
            serverId:$serverId,
            state:created,
        ) {
            state
        }
    }
`

type ServerControlsProps = {
  server?: Server
};

const ServerStopButton = ({ server }: ServerControlsProps) => {
  const [enqueue, { data, loading, error }] = useMutation(ENQUEUE_SERVER_STOP)

  const errorDisplay = <h1>Error loading server info!</h1>

  if (!server) return errorDisplay

  if (loading) return (<p>🕜Enqueueing stop...</p>)
  if (error) return (<p>❌Enqueueing stop failed</p>)

  const serverLatestStateIsStopping = (server.latestLog && (server.latestLog.state === 'stop_queued' || server.latestLog.state === 'stop_started'))
  const serverId = server.id

  const stopButton = (
    <button className="bg-red-600 hover:bg-red-700 text-gray-50 px-4 py-3 rounded-full" onClick={e => {
      e.preventDefault()
      enqueue({ variables: { serverId } })
    }}>Stop</button>
  )

  const stopEnqueued = data && data.server && data.server.latestLog && (data.server.latestLog.state === 'stop_queued')
  if (serverLatestStateIsStopping || stopEnqueued) return (<p>✅Stop enqueued!</p>)
  if (server.latestLog && server.latestLog.state === 'started') return stopButton
  return (null)
}

const ServerStartButton = ({ server }: ServerControlsProps) => {
  const [enqueue, { data, loading, error }] = useMutation(ENQUEUE_SERVER_START)

  const errorDisplay = <h1>Error loading server info!</h1>

  if (!server) return errorDisplay

  if (loading) return (<p>🕜Enqueueing start...</p>)
  if (error) return (<p>❌Enqueueing start failed</p>)

  const serverLatestStateIsStarted = (server.latestLog && server.latestLog.state === 'started')
  if (serverLatestStateIsStarted) return (null)

  const serverLatestStateIsStarting = (server.latestLog && (server.latestLog.state === 'created' || server.latestLog.state === 'start_started'))
  const serverId = server.id

  const startButton = (
    <button className="bg-green-600 hover:bg-green-700 text-gray-50 px-4 py-3 rounded-full" onClick={e => {
      e.preventDefault()
      enqueue({ variables: { serverId } })
    }}>Start</button>
  )

  const startEnqueued = data && data.server && data.server.latestLog && (data.server.latestLog.state === 'start_started')
  if (serverLatestStateIsStarting || startEnqueued) return (<p>✅Start enqueued!</p>)
  if (server.latestLog && server.latestLog.state === 'stopped') return startButton
  return (null)
}

const ServerControls = ({ server }: ServerControlsProps) => {
  return (
    <div>
      <ServerStartButton server={server} />
      <ServerStopButton server={server} />
    </div>
  )
}

export default ServerControls
