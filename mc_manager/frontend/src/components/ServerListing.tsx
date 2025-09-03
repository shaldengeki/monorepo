import _ from 'lodash'
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom'

import { displayLog, displayServerUrl } from '../Utils'
import Table from '../../../../react_library/Table';

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

type ServerListingTableRow = {
    "ID": React.JSX.Element,
    "Created": React.JSX.Element,
    "Created by": React.JSX.Element,
    "Name": React.JSX.Element,
    "URL": React.JSX.Element,
    "Mod": React.JSX.Element,
    "Status": React.JSX.Element,

}

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
    pollInterval: 60_000
  })

  const loadingDisplay = <h1>Loading servers...</h1>
  const errorDisplay = <h1>Error loading servers!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  const formattedServers : Array<ServerListingTableRow> = _.map(data.servers || [], (server) => {
    const createdFormatted = new Date(server.created * 1000).toLocaleDateString('en-US')
    const serverLink = (
      <Link to={`/servers/${server.name}`} className="text-blue-400">
        {server.name}
      </Link>
    )

    return {
      "ID": <p>{server.id}</p>,
      "Created": <p>{createdFormatted}</p>,
      "Created by": <p>{server.createdBy}</p>,
      "Name": serverLink,
      "URL": <p>{displayServerUrl(server.port)}</p>,
      "Mod": <p>{server.zipfile}</p>,
      "Status": <p>{displayLog(server.latestLog)}</p>
    }
  })
  return (
        <Table<ServerListingTableRow> rows={formattedServers} keyName='servers' />
  )
}

export default ServerListing
