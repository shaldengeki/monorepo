import Activity from "./Activity";

type User = {
    fitbitUserId: string;
    displayName: string;
    createdAt: number;
    activities: Activity[];
}

export const emptyUser: User = {
    fitbitUserId: 'empty-user',
    displayName: 'emptyUser',
    createdAt: 0,
    activities: []
}

export default User;
