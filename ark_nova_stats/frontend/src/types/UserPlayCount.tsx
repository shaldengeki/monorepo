import User, {emptyUser} from './User';
import Card, {emptyCard} from './Card';

type UserPlayCount = {
    user: User;
    card: Card;
    count: number;
}

export const emptyUserPlayCount: UserPlayCount = {
    user: emptyUser,
    card: emptyCard,
    count: 0,
}

export default UserPlayCount;
