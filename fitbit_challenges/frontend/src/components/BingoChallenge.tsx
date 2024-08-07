import React, {useState} from 'react';
import _ from 'lodash'
import { gql } from '@apollo/client/core';
import { useQuery, useMutation } from '@apollo/client/react/hooks';

import User from '../types/User';
import BingoCard, {BingoTile, emptyBingoTile} from '../types/Bingo';
import {UserLeaderboardHeader} from './UserLeaderboard';

export const FETCH_BINGO_QUERY = gql`
    query FetchBingo($id: Int!) {
          bingoChallenge(id: $id) {
              id
              users {
                fitbitUserId
                displayName
              }
              createdAt
              startAt
              endAt
              ended
              sealed
              sealAt
              bingoCards {
                id
                user {
                    fitbitUserId
                    displayName
                }
                rows
                columns
                tiles {
                    id
                    steps
                    activeMinutes
                    distanceKm
                    coordinateX
                    coordinateY
                    flipped
                    flippedAt
                    requiredForWin
                }
                finished
                finishedAt
              }
              unusedAmounts {
                steps
                activeMinutes
                distanceKm
              }
          }
      }
`;

export const FLIP_BINGO_TILE_MUTATION = gql`
    mutation FlipBingoTile($id: Int!) {
        flipBingoTile(id: $id) {
            id
            flipped
            bingoCard {
                challenge {
                    unusedAmounts {
                        steps
                        activeMinutes
                        distanceKm
                    }
                }
            }
        }
    }
`

type IconProps = {
    paths: string[]
    strokeWidth?: number
    viewBox?: string
    stroke?: string
}

const Icon = ({paths, strokeWidth, viewBox, stroke}: IconProps) => {
    strokeWidth = strokeWidth || 0.1;
    viewBox = viewBox || "0 0 16 16";
    stroke = stroke || "currentColor";
    const pathElts = paths.map((path, idx) => <path key={idx} strokeLinecap="round" strokeLinejoin="round" d={path} />);
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox={viewBox}
            strokeWidth={strokeWidth}
            stroke={stroke}
            className="w-1/2 h-1/2 mx-auto"
        >
            {pathElts}
        </svg>
    );
}

const FlippedIcon = () => {
    return <Icon
        stroke="green"
        paths={[
            "M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z",
            "M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z",
        ]}
    />
}

const StepsIcon = () => {
    return <Icon paths={["M6 12.796V3.204L11.481 8 6 12.796zm.659.753 5.48-4.796a1 1 0 0 0 0-1.506L6.66 2.451C6.011 1.885 5 2.345 5 3.204v9.592a1 1 0 0 0 1.659.753z"]} />;
}

const ActiveMinutesIcon = () => {
    return <Icon paths={["M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09zM4.157 8.5H7a.5.5 0 0 1 .478.647L6.11 13.59l5.732-6.09H9a.5.5 0 0 1-.478-.647L9.89 2.41 4.157 8.5z"]} />;
}

const DistanceKmIcon = () => {
    return <Icon
        paths={[
            "M12.166 8.94c-.524 1.062-1.234 2.12-1.96 3.07A31.493 31.493 0 0 1 8 14.58a31.481 31.481 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304 7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94zM8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10z",
            "M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
        ]} />;
}

type BingoChallengeTileProps = {
    tile: BingoTile
    challengeId: number
    isCurrentUser: boolean
    challengeEnded: boolean
}

const BingoChallengeTile = ({tile, challengeId, isCurrentUser, challengeEnded}: BingoChallengeTileProps) => {
    const [
        flipTile
    ] = useMutation(
        FLIP_BINGO_TILE_MUTATION,
        {
            refetchQueries: [
                {
                    query: FETCH_BINGO_QUERY,
                    variables: {
                        id: challengeId
                    }
                },
                'FetchBingo'
            ]
        }
    );

    let icon = <p />;
    let text = "";
    let backgroundColor = "";
    if (tile.flipped) {
        icon = <FlippedIcon />
        if (tile.steps !== null) {
            text = `${tile.steps} steps`
        } else if (tile.activeMinutes !== null) {
            text = `${tile.activeMinutes} min`
        } else if (tile.distanceKm !== null) {
            text = `${tile.distanceKm} km`
        }
    } else if (tile.steps !== null) {
        icon = <StepsIcon />
        text = `${tile.steps}`;
        backgroundColor = "bg-teal-500 dark:bg-teal-800"
    } else if (tile.activeMinutes !== null) {
        icon = <ActiveMinutesIcon />;
        text = `${tile.activeMinutes}`;
        backgroundColor = "bg-pink-400 dark:bg-pink-900"
    } else if (tile.distanceKm !== null) {
        icon = <DistanceKmIcon />;
        text = `${tile.distanceKm}`;
        backgroundColor = "bg-blue-400 dark:bg-violet-800"
    }
    const className = `flex items-center rounded-full aspect-square font-extrabold text-white dark:text-slate-50 ${backgroundColor}`
    return (
        <div className={className} onClick={(e) => {
            e.preventDefault();
            if (!isCurrentUser || tile.flipped || challengeEnded) {
                return;
            }
            flipTile({
                variables: {
                    id: tile.id
                }
            })
        }}>
            <span>
                {icon}
                <p>{text}</p>
            </span>
        </div>
    );
}

type BingoChallengeUnusedAmountsProps = {
    steps: number;
    activeMinutes: number;
    distanceKm: number;
}

const BingoChallengeUnusedAmounts = ({steps, activeMinutes, distanceKm}: BingoChallengeUnusedAmountsProps) => {
    return (
        <div className="grid grid-cols-3 content-center text-left py-4">
            <div className="flex">
                <div className="w-1/3 my-auto">
                    <StepsIcon />
                </div>
                <div className="w-2/3 my-auto">
                    <p>{steps}</p>
                    <p>Steps</p>
                </div>
            </div>
            <div className="flex">
                <div className="w-1/3 my-auto">
                    <ActiveMinutesIcon />
                </div>
                <div className="w-2/3 my-auto">
                    <p>{activeMinutes}</p>
                    <p>Active Minutes</p>
                </div>
            </div>
            <div className="flex">
                <div className="w-1/3 my-auto">
                    <DistanceKmIcon />
                </div>
                <div className="w-2/3 my-auto">
                    <p>{distanceKm}</p>
                    <p>Km</p>
                </div>
            </div>
        </div>
    )
}

type BingoChallengeCardProps = {
    card: BingoCard
    user: User
    currentUser: User
    challengeId: number
    challengeEnded: boolean
}

const BingoChallengeCard = ({card, user, currentUser, challengeId, challengeEnded}: BingoChallengeCardProps) => {
    const tiles = card.tiles.map(
        (tile) => <BingoChallengeTile
                    key={tile.id}
                    tile={tile}
                    challengeId={challengeId}
                    isCurrentUser={currentUser === user}
                    challengeEnded={challengeEnded}
                />
    );
    return (
        <div className="grid grid-cols-5 grid-rows-5 gap-1 text-center">
            {tiles}
        </div>
    )
}

type BingoChallengeLeaderboardTileProps = {
    tile: BingoTile
}

const BingoChallengeLeaderboardTile = ({tile}: BingoChallengeLeaderboardTileProps) => {
    let backgroundColor = "bg-slate-400";
    if (tile.flipped) {
        if (tile.requiredForWin) {
            backgroundColor = "bg-green-500";
        } else {
            backgroundColor = "bg-yellow-900"
        }
    }
    const className = `flex items-center rounded-full aspect-square font-extrabold text-white dark:text-slate-50 text-xl ${backgroundColor}`
    return (
        <div className={className} />
    );
}

type BingoChallengeLeaderboardCardProps = {
    card: BingoCard
    setUserHook: Function
    isDisplayedCard: boolean
    place: number
}

const BingoChallengeLeaderboardCard = ({card, setUserHook, isDisplayedCard, place}: BingoChallengeLeaderboardCardProps) => {
    const tiles = card.tiles.map((tile) => <BingoChallengeLeaderboardTile key={tile.id} tile={tile} />);
    const baseClasses = (isDisplayedCard) ? "rounded border border-green-500" : "";
    let displayText = "";
    if (card.finished) {
        if (place === 1) {
            displayText = "🥇";
        } else if (place === 2) {
            displayText = "🥈";
        } else if (place === 3) {
            displayText = "🥉";
        }
    }
    displayText = `${displayText}${card.user.displayName}`

    return (
        <div className={`${baseClasses} p-1`} onClick={(e) => {setUserHook(card.user)}}>
            <div className="grid grid-cols-5 grid-rows-5 gap-1 text-center">
                {tiles}
            </div>
            <p className="text-center">{displayText}</p>
        </div>
    )
}

type BingoChallengeLeaderboardProps = {
    cards: BingoCard[]
    setUserHook: Function
    displayedCard: BingoCard
}

const BingoChallengeLeaderboard = ({cards, setUserHook, displayedCard}: BingoChallengeLeaderboardProps) => {
    const sortedCards = cards.map((card: BingoCard, idx) => {
            return <BingoChallengeLeaderboardCard key={card.id} card={card} setUserHook={setUserHook} isDisplayedCard={displayedCard.id === card.id} place={idx+1} />
        })

    return (
        <div className="text-center">
            <h1 className="text-xl">Leaderboard</h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {sortedCards}
            </div>
        </div>
    )
}

type BingoVictoryPatternProps = {
    card: BingoCard
}

const BingoVictoryPattern = ({card}: BingoVictoryPatternProps) => {
    const tiles = card.tiles.map(
        (tile) => {
            return {
                ...emptyBingoTile,
                coordinateX: tile.coordinateX,
                coordinateY: tile.coordinateY,
                requiredForWin: tile.requiredForWin,
                flipped: tile.requiredForWin
            }
        }
    ).map(
        (tile) => <BingoChallengeLeaderboardTile key={tile.id} tile={tile} />
    );
    return (
        <div className="grid grid-cols-5 grid-rows-5 gap-1 text-center">
            {tiles}
        </div>
    )
}

type BingoChallengeProps = {
    id: number;
    currentUser: User;
}

type CardPlace = {
    card: BingoCard
    place: number
}

const BingoChallenge = ({id, currentUser}: BingoChallengeProps) => {
    const [displayedUser, setDisplayedUser] = useState<User>(currentUser);
    const {loading, error, data } = useQuery(
        FETCH_BINGO_QUERY,
        {variables: { id }},
    );
    if (loading) {
        return <p>Loading...</p>
    }
    if (error) {
        return <p>Error loading bingo challenge!</p>
    }
    if (!data.bingoChallenge) {
        return <p>Could not find a bingo challenge with that ID!</p>
    }

    const cards: Array<BingoCard> = data.bingoChallenge.bingoCards;
    const sortedCards = _.orderBy(
        _.map(
            cards,
            (card) => {
                const flipped = card.tiles.filter((tile) => tile.flipped && tile.requiredForWin);
                return {
                    card,
                    finished: card.finished,
                    flipped,
                    finishedAt: card.finishedAt
                }
            }
        ),
        ['finished', 'flipped', 'finishedAt'],
        ['desc', 'desc', 'asc'],
    ).map((cardData) => cardData.card);

    const displayedCard = sortedCards.filter(
        (card) => card.user.fitbitUserId === displayedUser.fitbitUserId
    )[0];

    const currentUserPlaces = sortedCards.map(
        (card, idx) => { return {card, place: idx + 1} }
    ).filter(
        (c: CardPlace) => c.card.user.fitbitUserId === currentUser.fitbitUserId && c.card.finished
    ).map(
        (c: CardPlace) => c.place
    );
    const currentUserPlace = currentUserPlaces.length > 0 ? currentUserPlaces[0] : null;

    let finishingText = "";
    if (currentUserPlace) {
        if (data.bingoChallenge.ended) {
            finishingText = "🎉Congrats on finishing!🎉 The challenge is now over.";
        } else {
            finishingText = "🎉Congrats on finishing!🎉 You can keep flipping tiles.";
        }
    } else if (data.bingoChallenge.ended) {
        finishingText = "This challenge is now over.";
    }

    return (
        <div>
            <UserLeaderboardHeader
                title="Bingo"
                id={data.bingoChallenge.id}
                startAt={data.bingoChallenge.startAt}
                endAt={data.bingoChallenge.endAt}
                ended={data.bingoChallenge.ended}
                sealAt={data.bingoChallenge.sealAt}
                sealed={data.bingoChallenge.sealed}
            />
            <div className="grid grid-cols-4 space-y-6">
                <div className="col-span-4 md:col-span-2 space-y-3">
                    { finishingText && <p className="text-center text-xl font-bold">{finishingText}</p>}
                    <BingoChallengeUnusedAmounts
                        steps={data.bingoChallenge.unusedAmounts.steps}
                        activeMinutes={data.bingoChallenge.unusedAmounts.activeMinutes}
                        distanceKm={data.bingoChallenge.unusedAmounts.distanceKm}
                    />
                    <BingoChallengeCard
                        card={displayedCard}
                        user={displayedUser}
                        currentUser={currentUser}
                        challengeId={id}
                        challengeEnded={data.bingoChallenge.ended}
                    />
                    <div className="grid grid-cols-3">
                        <div className="col-start-2 col-end-3">
                            <BingoVictoryPattern card={displayedCard} />
                        </div>
                    </div>
                </div>
                <div className="col-span-4 md:col-span-2 px-24 md:px-4">
                    <BingoChallengeLeaderboard cards={sortedCards} setUserHook={setDisplayedUser} displayedCard={displayedCard} />
                </div>
            </div>
        </div>
    )
};

export default BingoChallenge;
