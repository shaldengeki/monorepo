import * as React from 'react'
import _ from 'lodash'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'
import { Link } from 'react-router-dom'

import { timeAgo, serverLogStatusSymbol } from '../Utils'
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
    },
    pollInterval: 10_000
  })

  const loadingDisplay = <h1>Loading servers...</h1>
  const errorDisplay = <h1>Error loading servers!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const formattedServers : Array<ServerRow> = _.map(data.servers || [], (server) => {
    const createdFormatted = new Date(server.created * 1000).toLocaleDateString('en-US')
    const updated = timeAgo(server.latestLog.created)
    const serverLink = (
      <Link to={`/servers/${server.name}`} className="text-blue-400">
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
      latestState: `${serverLogStatusSymbol(server.latestLog.state)} ${server.latestLog.state}`
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
