import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import EmuCupTableIds from '../EmuCupTableIds';
import GameLog from '../types/GameLog';
import GameLogsTable from '../components/GameLogsTable';
import PageLink from '../components/PageLink';
import TournamentResultsTable from '../components/TournamentResultsTable';

export const EMU_CUP_VIEW_QUERY = gql`
    query EmuCupView($tableIds: [Int]) {
        gameLogs(bgaTableIds: $tableIds) {
            bgaTableId
            users {
                bgaId
                name
            }
            start
            end
            gameRatingChanges {
                user {
                    bgaId
                    name
                }
                priorElo
                newElo
            }
            statistics {
                user {
                    bgaId
                    name
                }
                rank
            }
        }
    }
`;

const EmuCupView = () => {
    const { loading, error, data } = useQuery(
        EMU_CUP_VIEW_QUERY,
        {
            variables: {tableIds: EmuCupTableIds}
        }
    );


    let innerContent = <p></p>;
    if (loading) innerContent = <p>Loading...</p>;
    else if (error) innerContent = <p>Error: {error.message}</p>;
    else {
        const gameLogs: GameLog[] = data.gameLogs;
        if (!gameLogs || gameLogs.length === 0) {
            innerContent = <p>No games found!</p>
        } else {
            // TODO
            const sortedGameLogs = gameLogs.toSorted((a, b) => { return ((a.end || 0) > (b.end || 0)) ? -1 : (a.end === b.end) ? 0 : 1 });
            innerContent = (<div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Results:</h2>
                    <TournamentResultsTable gameLogs={gameLogs} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Stats:</h2>
                    {/* <TournamentStatisticsTable statistics={statistics} /> */}
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>All games:</h2>
                    <GameLogsTable gameLogs={sortedGameLogs} />
                </div>
            </div>);
        }
    }

    return (
        <PageContainer>
            <div>
                <PageTitle linkTo={'/emu_cup'}>Emu Cup</PageTitle>
                <p>Not sure what this is? <PageLink to={'https://www.youtube.com/watch?v=Rf_iUSZZqgM'}>See the first 4.5min of this video.</PageLink></p>
                {innerContent}
            </div>
        </PageContainer>
    )
}

export default EmuCupView;
