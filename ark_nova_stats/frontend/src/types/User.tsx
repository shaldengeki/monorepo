import GameLog from './GameLog';

type User = {
    id: number;
    bgaId: number;
    name: string;
    avatar: string;
    gameLogs: GameLog[];
    numGameLogs: number;
}

export const emptyUser: User = {
    id: 0,
    bgaId: 0,
    name: "",
    avatar: "",
    gameLogs: [],
    numGameLogs: 0,
}

export default User;
