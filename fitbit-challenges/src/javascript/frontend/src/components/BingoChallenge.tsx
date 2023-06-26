import React, {useState} from 'react';
import _ from 'lodash'
import { useQuery, gql } from '@apollo/client';

import PageTitle from './PageTitle';
import Activity, {ActivityDelta, ActivityTotal, emptyActivity, emptyActivityDelta} from '../types/Activity';
import User from '../types/User';
import BingoCard, {BingoTile} from '../types/Bingo';

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
              bingoCards {
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
                    requiredForWin
                }
              }
              unusedAmounts {
                steps
                activeMinutes
                distanceKm
              }
          }
      }
`;

type IconProps = {
    paths: string[]
    strokeWidth?: number
    viewBox?: string
}

const Icon = ({paths, strokeWidth, viewBox}: IconProps) => {
    strokeWidth = strokeWidth || 0.1;
    viewBox = viewBox || "0 0 16 16";
    const pathElts = paths.map((path, idx) => <path key={idx} strokeLinecap="round" strokeLinejoin="round" d={path} />);
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox={viewBox}
            strokeWidth={strokeWidth}
            stroke="currentColor"
            className="w-1/2 h-1/2 mx-auto"
        >
            {pathElts}
        </svg>
    );
}

// TODO: pick better icons for steps & distance
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
}

const BingoChallengeTile = ({tile}: BingoChallengeTileProps) => {
    let icon = <p />;
    let text = "";
    if (tile.steps !== null) {
        icon = <StepsIcon />
        text = `${tile.steps}`;
    } else if (tile.activeMinutes !== null) {
        icon = <ActiveMinutesIcon />;
        text = `${tile.activeMinutes}`;
    } else if (tile.distanceKm !== null) {
        icon = <DistanceKmIcon />;
        text = `${tile.distanceKm}`;
    }
    if (text === "0") {
        console.log("Tile", tile);
    }
    const className = `flex items-center rounded-full aspect-square font-extrabold text-white dark:text-slate-50 text-xl bg-blue-400 dark:bg-indigo-800`
    return (
        <div className={className}>
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
                <div className="w-2/3">
                    <div>{steps}</div>
                    <p>Steps</p>
                </div>
            </div>
            <div className="flex">
                <div className="w-1/3 my-auto">
                    <ActiveMinutesIcon />
                </div>
                <div className="w-2/3">
                    <div>{activeMinutes}</div>
                    <p>Active Minutes</p>
                </div>
            </div>
            <div className="flex">
                <div className="w-1/3 my-auto">
                    <DistanceKmIcon />
                </div>
                <div className="w-2/3">
                    <div>{distanceKm}</div>
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
}

const BingoChallengeCard = ({card, user, currentUser}: BingoChallengeCardProps) => {
    const tiles = card.tiles.map((tile) => <BingoChallengeTile key={tile.id} tile={tile} />);
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
    const displayedCard = cards.filter(
        (card) => card.user.fitbitUserId === displayedUser.fitbitUserId
    )[0];

    return (
        <div>
            <PageTitle className="text-center">Bingo</PageTitle>
            <BingoChallengeUnusedAmounts
                steps={data.bingoChallenge.unusedAmounts.steps}
                activeMinutes={data.bingoChallenge.unusedAmounts.activeMinutes}
                distanceKm={data.bingoChallenge.unusedAmounts.distanceKm}
            />
            <BingoChallengeCard
                card={displayedCard}
                user={displayedUser}
                currentUser={currentUser}
            />
        </div>
    )
};

export default BingoChallenge;
