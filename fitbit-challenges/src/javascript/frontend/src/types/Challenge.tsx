import Activity from "./Activity";
import User from "./User";

export enum ChallengeType {
    WorkweekHustle = 0,
    WeekendWarrior = 1,
    Bingo = 2,
}

type Challenge = {
    id: number
    challengeType: ChallengeType
    users: User[]
    createdAt: number
    startAt: number
    started: boolean
    endAt: number
    ended: boolean
    sealAt: number
    sealed: boolean
    activities: Activity[]
    currentUserPlacement?: number
}

export const emptyChallenge: Challenge = {
    id: 0,
    challengeType: ChallengeType.WorkweekHustle,
    users: [],
    createdAt: 0,
    startAt: 0,
    started: false,
    endAt: 0,
    ended: false,
    sealAt: 0,
    sealed: false,
    activities: [],
}

export default Challenge;
