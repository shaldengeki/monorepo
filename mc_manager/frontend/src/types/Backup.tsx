type Backup = {
    id?: number,
    created: number,
    state: string,
    error?: string,
    remotePath?: string
  }

export default Backup
