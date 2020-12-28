import type Backup from './types/Backup'
import type Log from './types/Log'

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
  } else if (status === 'created') {
    return '🚧'
  } else if (status === 'restore_queued') {
    return '⏳'
  } else if (status === 'restore_started') {
    return '🚧'
  } else if (status === 'stopped') {
    return '🔴'
  } else {
    return '❓'
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
  } else {
    return '❓'
  }
}

export const displayBackup = ({ created, state }: Backup): string => {
  return `${serverBackupStatusSymbol(state)} ${state}, ${timeAgo(created)}`
}

export const displayLog = ({ created, state }: Log): string => {
  return `${serverLogStatusSymbol(state)} ${state} ${timeAgo(created)}`
}
