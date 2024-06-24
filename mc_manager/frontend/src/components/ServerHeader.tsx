import * as React from 'react'

type ServerHeaderProps = {
    name: string
};

const ServerHeader = ({ name }: ServerHeaderProps) => {
  return (
        <p className="text-4xl">{name}</p>
  )
}

export default ServerHeader
