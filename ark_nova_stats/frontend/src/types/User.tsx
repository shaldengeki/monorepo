type User = {
    id: number;
    bgaId: number;
    name: string;
    avatar: string;
    numGameLogs: number;
    currentElo?: number;
    currentArenaElo?: number;
}

export const emptyUser: User = {
    id: 0,
    bgaId: 0,
    name: "",
    avatar: "",
    numGameLogs: 0,
}

export default User;
