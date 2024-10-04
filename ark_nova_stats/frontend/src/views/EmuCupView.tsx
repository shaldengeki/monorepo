import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
import EmuCupTableIds from '../EmuCupTableIds';
import GameLog from '../types/GameLog';
import GameStatistics from '../types/GameStatistics';
import GameLogsTable from '../components/GameLogsTable';

export const EMU_CUP_VIEW_QUERY = gql`
    query EmuCupView($tableIds: [String]) {
        gameLogs(bgaTableIds: $tableIds) {
            bgaTableId
            users {
                bgaId
                name
            }
            cards {
                name
                bgaId
            }
            start
            end
            gameRatingChanges {
                gameLog {
                    bgaTableId
                }
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
                score
                thinkingTime
                startingPosition
                breaksTriggered
                triggeredEnd
                mapId
                actionsBuild
                actionsAnimals
                actionsCards
                actionsAssociation
                actionsSponsors
                xTokensGained
                xActions
                xTokensUsed
                moneyGained
                moneyGainedThroughIncome
                moneySpentOnAnimals
                moneySpentOnEnclosures
                moneySpentOnDonations
                moneySpentOnPlayingCardsFromReputationRange
                cardsDrawnFromDeck
                cardsDrawnFromReputationRange
                cardsSnapped
                cardsDiscarded
                playedSponsors
                playedAnimals
                releasedAnimals
                associationWorkers
                associationDonations
                associationReputationActions
                associationPartnerZooActions
                associationUniversityActions
                associationConservationProjectActions
                builtEnclosures
                builtKiosks
                builtPavilions
                builtUniqueBuildings
                hexesCovered
                hexesEmpty
                upgradedActionCards
                upgradedAnimals
                upgradedBuild
                upgradedCards
                upgradedSponsors
                upgradedAssociation
                iconsAfrica
                iconsEurope
                iconsAsia
                iconsAustralia
                iconsAmericas
                iconsBird
                iconsPredator
                iconsHerbivore
                iconsBear
                iconsReptile
                iconsPrimate
                iconsPettingZoo
                iconsSeaAnimal
                iconsWater
                iconsRock
                iconsScience
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
            const statistics: GameStatistics[] = data.gameLogs.map((gameLog: any) => {return gameLog.statistics}).flatMap();
            const sortedGameLogs = gameLogs.sort((a, b) => { return ((a.end || 0) > (b.end || 0)) ? -1 : (a.end == b.end) ? 0 : 1 });
            innerContent = (<div>
                <div className={"py-2"}>
                    <h2 className={"text-xl"}>Results:</h2>
                    {/* <TournamentResultsTable statistics={statistics} /> */}
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
                <PageTitle>Emu Cup</PageTitle>
                <p>Not sure what this is? <Link to={'https://www.youtube.com/watch?v=Rf_iUSZZqgM'}>See the first 4.5min of this video.</Link></p>
                {innerContent}
            </div>
        </PageContainer>
    )
}

export default EmuCupView;
