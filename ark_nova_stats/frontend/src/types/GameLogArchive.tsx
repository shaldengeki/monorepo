import GameLog, {emptyGameLog} from "./GameLog";

type GameLogArchive = {
    id: number;
    archiveType: string;
    url: string;
    sizeBytes: number;
    numGameLogs: number;
    numUsers: number;
    maxGameLog: GameLog;
    createdAt: number;
}

export const emptyGameLogArchive: GameLogArchive = {
    id: 0,
    archiveType: "",
    url: "",
    sizeBytes: 0,
    numGameLogs: 0,
    numUsers: 0,
    maxGameLog: emptyGameLog,
    createdAt: 0,
}

export default GameLogArchive;
