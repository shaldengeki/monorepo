import type Backup from './Backup'

type Log = {
    created: number,
    state: string,
    error?: string,
    backup?: Backup
}

export default Log
