import User, { emptyUser } from './User';

type UserRatingChange = {
    user: User;
    priorElo: number;
    newElo: number;
    priorArenaElo: number | null | undefined;
    newArenaElo: number | null | undefined;
}

export const emptyUserRatingChange: UserRatingChange = {
    user: emptyUser,
    priorElo: 1300,
    newElo: 1300,
    priorArenaElo: undefined,
    newArenaElo: undefined,
}

export default UserRatingChange;
