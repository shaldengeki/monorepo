import GameLog from './GameLog';

type User = {
    id: number;
    bgaId: number;
    name: string;
    avatar: string;
    recentGameLogs: GameLog[];
    numGameLogs: number;
}

export const emptyUser: User = {
    id: 0,
    bgaId: 0,
    name: "",
    avatar: "",
    recentGameLogs: [],
    numGameLogs: 0,
}

export default User;
