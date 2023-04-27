import Activity from "./Activity";

type Challenge = {
    id: number
    users: string[]
    createdAt: number
    startAt: number
    endAt: number
    ended: boolean
    sealAt: number
    sealed: boolean
    activities: Activity[]
}

export const EmptyChallenge: Challenge = {
    id: 0,
    users: [],
    createdAt: 0,
    startAt: 0,
    endAt: 0,
    ended: false,
    sealAt: 0,
    sealed: false,
    activities: [],
}

export default Challenge;
