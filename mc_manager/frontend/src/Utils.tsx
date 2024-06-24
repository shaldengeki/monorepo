import type Backup from './types/Backup'
import type Log from './types/Log'

const { REACT_APP_API_HOST = 'localhost' } = process.env

export const timeAgo = (epochTime: number): string => {
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

export const serverLogStatusSymbol = (status: string): string => {
  if (status === 'started') {
    return '🟢'
  } else if (status === 'start_started') {
    return '⏳'
  } else if (status === 'created') {
    return '🚧'
  } else if (status === 'restore_queued') {
    return '⏳'
  } else if (status === 'restore_started') {
    return '🚧'
  } else if (status === 'stop_queued') {
    return '🧨'
  } else if (status === 'stop_started') {
    return '🚨'
  } else if (status === 'stopped') {
    return '🔴'
  } else {
    return '❓'
  }
}

export const serverLogStatusVerb = (status: string): string => {
  if (status === 'started') {
    return 'running'
  } else if (status === 'start_started') {
    return 'queueing server start'
  } else if (status === 'created') {
    return 'initializing'
  } else if (status === 'restore_queued') {
    return 'queueing restoration from backup'
  } else if (status === 'restore_started') {
    return 'restoring backup'
  } else if (status === 'stop_queued') {
    return 'queueing stop'
  } else if (status === 'stop_started') {
    return 'stop in progress'
  } else if (status === 'stopped') {
    return 'stopped'
  } else {
    return 'unknown'
  }
}

export const serverBackupStatusSymbol = (status: string): string => {
  if (status === 'completed') {
    return '🟢'
  } else if (status === 'created') {
    return '🚧'
  } else if (status === 'started') {
    return '🚧'
  } else if (status === 'failed') {
    return '🔴'
  } else if (status === 'deleted') {
    return '🗑'
  } else {
    return '❓'
  }
}

export const displayBackup = (backup?: Backup): string => {
  if (!backup) return ''
  const { created, state } = backup
  return `${serverBackupStatusSymbol(state)} ${state}, ${timeAgo(created)}`
}

export const displayLog = (log?: Log): string => {
  if (!log) return ''
  const { created, state } = log
  return `${serverLogStatusSymbol(state)} ${serverLogStatusVerb(state)} ${timeAgo(created)}`
}

export const displayServerUrl = (port: number): string => {
  return `${REACT_APP_API_HOST}:${port}`
}
