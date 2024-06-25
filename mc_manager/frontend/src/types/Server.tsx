import type Backup from './Backup'
import type Log from './Log'

type Server = {
    id?: number,
    created: number,
    createdBy: string,
    name: string,
    port: number,
    timezone: string,
    zipfile: string,
    motd: string,
    memory: string,
    logs?: Log[],
    latestLog?: Log,
    backups?: Backup[],
    latestBackup?: Backup
  }

export default Server
