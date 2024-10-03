import React from 'react';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';
// import { Link } from 'react-router-dom';

import PageContainer from '../components/PageContainer';
import PageTitle from "../components/PageTitle";
// import Table from '../components/Table';
import EmuCupTableIds from '../EmuCupTableIds';
import GameLog from '../types/GameLog';
import GameStatistics from '../types/GameStatistics';

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
        const statistics: GameStatistics[] = data.gameLogs.map((gameLog: any) => {return gameLog.statistics}).flatMap();

        if (!gameLogs || gameLogs.length === 0) {
            innerContent = <p>No games found!</p>
        } else {
            // TODO
            // <TournamentResultsTable statistics={statistics} />
        }
    }

    return (
        <PageContainer>
            <div>
                <PageTitle>Emu Cup</PageTitle>
                {innerContent}
            </div>
        </PageContainer>
    )
}

export default EmuCupView;
