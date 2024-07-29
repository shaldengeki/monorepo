type Stats = {
    numGameLogs: number;
    numPlayers: number;
    mostRecentSubmission: number | null;
}

export const emptyStats: Stats = {
    numGameLogs: 0,
    numPlayers: 0,
    mostRecentSubmission: null,
}

export const exampleStats: Stats = {
    numGameLogs: 52,
    numPlayers: 19,
    mostRecentSubmission: 2348723847,
}

export default Stats;
