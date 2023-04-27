type Activity = {
    id: number;
    user: string;
    createdAt: number;
    recordDate: string;
    steps: number;
    activeMinutes: number;
    distanceKm: number;
}

export const EmptyActivity: Activity = {
    id: 0,
    user: '',
    createdAt: 0,
    recordDate: '',
    steps: 0,
    activeMinutes: 0,
    distanceKm: 0,
}

export type ActivityDelta = {
    id: number;
    user: string;
    createdAt: number;
    recordDate: string;
    steps: number;
    stepsDelta: number;
    activeMinutes: number;
    activeMinutesDelta: number;
    distanceKm: number;
    distanceKmDelta: number;
}

export type ActivityTotal = {
    name: string;
    value: number;
    unit: string;
}

export default Activity;
