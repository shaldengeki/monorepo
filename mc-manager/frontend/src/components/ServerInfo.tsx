import * as React from 'react'

import type Server from '../types/Server'

import { timeAgo, displayBackup, displayLog, displayServerUrl } from '../Utils'

type ServerInfoProps = {server?: Server};

const ServerInfo = ({ server }: ServerInfoProps) => {
  const errorDisplay = <h1>Error loading server info!</h1>

  if (!server) return errorDisplay

  return (
    <div>
      <p className="text-3xl py-4">Info</p>
      <table className="table-auto border-collapse border">
        <tbody>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">Mod</td>
            <td className="border border-gray-300 px-4 py-2">{server.zipfile}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">Latest status</td>
            <td className="border border-gray-300 px-4 py-2">{displayLog(server.latestLog)}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">URL</td>
            <td className="border border-gray-300 px-4 py-2">{displayServerUrl(server.port)}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">Created</td>
            <td className="border border-gray-300 px-4 py-2">{timeAgo(server.created)}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">Creator</td>
            <td className="border border-gray-300 px-4 py-2">{server.createdBy}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">MOTD</td>
            <td className="border border-gray-300 px-4 py-2">{server.motd}</td>
          </tr>
          <tr>
            <td className="font-medium border border-gray-300 px-4 py-2">Latest backup</td>
            <td className="border border-gray-300 px-4 py-2">{displayBackup(server.latestBackup)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}

export default ServerInfo
