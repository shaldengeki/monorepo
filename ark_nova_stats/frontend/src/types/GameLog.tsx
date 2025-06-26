import GameStatistics from './GameStatistics';
import User from './User';
import UserRatingChange from './UserRatingChange';

type GameLog = {
    statistics?: GameStatistics[];
    id: number;
    log: string;
    bgaTableId: number;
    start?: number;
    end?: number;
    users: User[];
    gameRatingChanges: UserRatingChange[];
}

export const emptyGameLog: GameLog = {
    id: 0,
    log: "",
    bgaTableId: 0,
    start: 0,
    end: 0,
    users: [],
    gameRatingChanges: [],
}

export default GameLog;
