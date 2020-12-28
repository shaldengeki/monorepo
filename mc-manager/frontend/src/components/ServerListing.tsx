import * as React from 'react'
import _ from 'lodash'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'
import { Link } from 'react-router-dom'

import Table from './Table'

const GET_SERVERS = gql`
    query Servers(
        $earliestDate: Int,
        $latestDate: Int,
        $createdBy: String,
        $name: String,
        $port: Int,
        $timezone: String,
        $zipfile: String,
    ) {
        servers(
            earliestDate: $earliestDate,
            latestDate: $latestDate,
            createdBy: $createdBy,
            name: $name,
            port: $port,
            timezone: $timezone,
            zipfile: $zipfile,
        ) {
            id
            created
            createdBy
            name
            port
            zipfile
            latestLog {
                created
                state
            }
        }
    }
`

const timeAgo = (epochTime: number): string => {
  const happened = new Date(epochTime * 1000)
  const now = new Date()
  const diff = (now.getTime() - happened.getTime()) / 1000

  if (diff < 10) {
    return 'just now'
  } else if (diff < 60) {
    return Math.round(diff) + ' seconds ago'
  } else if (diff < (60 * 60)) {
    return Math.round(diff / 60) + ' minutes ago'
  } else if (diff < (60 * 60 * 24)) {
    return Math.round(diff / (60 * 60)) + ' hours ago'
  } else if (diff < (60 * 60 * 24 * 7)) {
    return Math.round(diff / (60 * 60 * 24)) + ' days ago'
  } else if (diff < (60 * 60 * 24 * 30)) {
    return Math.round(diff / (60 * 60 * 24 * 7)) + ' weeks ago'
  } else if (diff < (60 * 60 * 24 * 365)) {
    return Math.round(diff / (60 * 60 * 24 * 30)) + ' months ago'
  } else {
    return Math.round(diff / (60 * 60 * 24 * 365)) + ' years ago'
  }
}

type ServerRow = {
  id: string,
  created: string,
  createdBy: string,
  name: any,
  port: bigint,
  zipfile: string,
  latestUpdate: string,
  latestState: string
};

type ServerListingProps = {
  earliestDate?: bigint,
  latestDate?: bigint,
  createdBy?: string,
  name?: string,
  port?: bigint,
  timezone?: string,
  zipfile?: string
};

const ServerListing = ({
  earliestDate,
  latestDate,
  createdBy,
  name,
  port,
  timezone,
  zipfile
}: ServerListingProps) => {
  const { data, loading, error } = useQuery(GET_SERVERS, {
    variables: {
      earliestDate,
      latestDate,
      createdBy,
      name,
      port,
      timezone,
      zipfile
    }
  })

  const loadingDisplay = <h1>Loading servers...</h1>
  const errorDisplay = <h1>Error loading servers!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const formattedServers : Array<ServerRow> = _.map(data.servers || [], (server) => {
    const createdFormatted = new Date(server.created * 1000).toLocaleDateString('en-US')
    const updated = timeAgo(server.latestLog.created)
    const serverLink = (
      <Link to={`/servers/${server.name}`}>
        {server.name}
      </Link>
    )

    return {
      id: `${server.id}`,
      created: createdFormatted,
      createdBy: server.createdBy,
      name: serverLink,
      port: server.port,
      zipfile: server.zipfile,
      latestUpdate: updated,
      latestState: server.latestLog.state
    }
  })

  const cols = [
    'latestUpdate',
    'latestState',
    'name',
    'zipfile',
    'port',
    'createdBy',
    'created'
  ]
  return (
        <Table cols={cols} rows={formattedServers} key='servers' />
  )
}

export default ServerListing
