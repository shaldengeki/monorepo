type User = {
    id: number;
    bgaId: number;
    name: string;
    avatar: string;
}

export const emptyUser: User = {
    id: 0,
    bgaId: 0,
    name: "",
    avatar: "",
}

export default User;
