import React from 'react'
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

const ServerListing = (props) => {
  const {
    earliestDate,
    latestDate,
    createdBy,
    name,
    port,
    timezone,
    zipfile
  } = props
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

  const formattedServers = _.map(data.servers || [], (txn) => {
    const createdFormatted = new Date(txn.created * 1000).toLocaleDateString('en-US')
    const updatedFormatted = new Date(txn.latestLog.created * 1000).toLocaleDateString('en-US')
    return {
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
