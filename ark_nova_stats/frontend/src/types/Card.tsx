type Card = {
    id: number;
    name: string;
    bgaId: string;
    createdAt: number;
}

export const emptyCard: Card = {
    id: 0,
    name: "",
    bgaId: "",
    createdAt: 0,
}

export default Card;
