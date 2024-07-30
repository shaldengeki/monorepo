import User from './User';

type GameLog = {
    id: number;
    log: string;
    bgaTableId: number;
    users: User[];
}

export const emptyGameLog: GameLog = {
    id: 0,
    log: "",
    bgaTableId: 0,
    users: [],
}

export default GameLog;
