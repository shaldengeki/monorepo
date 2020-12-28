import * as React from 'react'
import { useQuery } from '@apollo/react-hooks'
import gql from 'graphql-tag'

const GET_SERVER = gql`
    query Servers($name: String) {
        servers(name: $name) {
            id
            created
            createdBy
            memory
            motd
            port
            zipfile
            logs {
                created
                state
                error
                backup {
                  created
                  state
                  error
                  remotePath
                }
            }
            latestLog {
                created
                state
                error
                backup {
                  created
                  state
                  error
                  remotePath
                }
            }
            backups {
                created
                state
                error
                remotePath
            }
            latestBackup {
                created
                state
                error
                remotePath
            }
        }
    }
`

type ServerInfoProps = {name: string};

const ServerInfo = ({ name }: ServerInfoProps) => {
  const { data, loading, error } = useQuery(GET_SERVER, {
    variables: { name }
  })

  const loadingDisplay = <h1>Loading server...</h1>
  const errorDisplay = <h1>Error loading server!</h1>

  if (loading) return loadingDisplay
  if (error) return errorDisplay

  return (
    <p>{data.servers[0].created}</p>
  )
}

export default ServerInfo
