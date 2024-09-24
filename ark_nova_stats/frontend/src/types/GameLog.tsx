import User from './User';
import UserRatingChange from './UserRatingChange';

type GameLog = {
    id: number;
    log: string;
    bgaTableId: number;
    users: User[];
    gameRatingChanges: UserRatingChange[];
}

export const emptyGameLog: GameLog = {
    id: 0,
    log: "",
    bgaTableId: 0,
    users: [],
    gameRatingChanges: [],
}

export default GameLog;
