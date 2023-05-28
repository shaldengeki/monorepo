import Activity from "./Activity";

export enum ChallengeType {
    WorkweekHustle = 0,
    WeekendWarrior = 1,
}

type Challenge = {
    id: number
    challengeType: ChallengeType
    users: string[]
    createdAt: number
    startAt: number
    endAt: number
    ended: boolean
    sealAt: number
    sealed: boolean
    activities: Activity[]
}

export const emptyChallenge: Challenge = {
    id: 0,
    challengeType: ChallengeType.WorkweekHustle,
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
