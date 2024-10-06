import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import EmuCupTableIds from '../EmuCupTableIds';
import PageLink from '../components/PageLink';
import TournamentResultsTable from '../components/TournamentResultsTable';
import GameStatistics from '../types/GameStatistics';

export const EMU_CUP_VIEW_QUERY = gql`
    query EmuCupView($tableIds: [Int]!) {
        gameRatings(bgaTableIds: $tableIds) {
            user {
                bgaId
                name
            }
            priorElo
            newElo
        }
        gameStatistics(bgaTableIds: $tableIds) {
            user {
                bgaId
                name
            }
            rank
            bgaTableId
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
        const statistics: GameStatistics[] = data.gameStatistics;
        if (!statistics || statistics.length === 0) {
            innerContent = <p>No games found!</p>
        } else {
            // TODO
            innerContent = (<div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Results:</h2>
                    <TournamentResultsTable statistics={statistics} />
                </div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Stats:</h2>
                    {/* <TournamentStatisticsTable statistics={statistics} /> */}
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
