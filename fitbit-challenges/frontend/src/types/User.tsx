import Activity from "./Activity";

type User = {
    fitbitUserId: string;
    displayName: string;
    createdAt: number;
    activities: Activity[];
}

export default User;
