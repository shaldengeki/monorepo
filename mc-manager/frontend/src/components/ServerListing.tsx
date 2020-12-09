import * as React from 'react'
import _ from 'lodash'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'

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
  name: string,
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

  const formattedServers : Array<ServerRow> = _.map(data.servers || [], (txn) => {
    const createdFormatted = new Date(txn.created * 1000).toLocaleDateString('en-US')
    const updatedFormatted = new Date(txn.latestLog.created * 1000).toLocaleDateString('en-US')
    return {
      id: `${txn.id}`,
      created: createdFormatted,
      createdBy: txn.createdBy,
      name: txn.name,
      port: txn.port,
      zipfile: txn.zipfile,
      latestUpdate: updatedFormatted,
      latestState: txn.latestLog.state
    }
  })

  const cols = [
    'created',
    'createdBy',
    'name',
    'port',
    'zipfile',
    'latestUpdate',
    'latestState'
  ]
  return (
        <Table cols={cols} rows={formattedServers} key='servers' />
  )
}

export default ServerListing
