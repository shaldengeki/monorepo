import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/react-testing';
import BingoChallenge, { FETCH_BINGO_QUERY } from './BingoChallenge';
import React from 'react';

import { emptyUser } from '../types/User';
import { emptyBingoCard, emptyBingoTile } from '../types/Bingo';

function mockFetchBingoQuery(result: object) {
    return {
        request: {
            query: FETCH_BINGO_QUERY,
            variables: {
                id: 1
            }
        },
        result
    }
}

it('should render a loading screen before data is loaded', async () => {
    const mock = mockFetchBingoQuery({
        data: {
            bingoChallenge: null
        }
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Loading...")).toBeInTheDocument();
});

it('should render an error when the query fails', async () => {
    const mock = mockFetchBingoQuery({
        errors: [
            {
                message: "Sample error"
            }
        ]
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Error loading bingo challenge!")).toBeInTheDocument();
});


it('should render an error when no challenge exists', async () => {
    const mock = mockFetchBingoQuery({
        data: {
            bingoChallenge: null
        }
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Could not find a bingo challenge with that ID!")).toBeInTheDocument();
});

it('should render a bingo header', async () => {
    const mock = mockFetchBingoQuery({
        data: {
            bingoChallenge: {
                id: 1,
                users: [
                    emptyUser,
                ],
                createdAt: 0,
                startAt: 0,
                endAt: 0,
                ended: false,
                bingoCards: [
                    emptyBingoCard,
                ],
                unusedAmounts: {
                    steps: 0,
                    activeMinutes: 0,
                    distanceKm: 0,
                }
            }
        }
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("Bingo")).toBeInTheDocument();
});

it('should render unused amounts', async () => {
    const mock = mockFetchBingoQuery({
        data: {
            bingoChallenge: {
                id: 1,
                users: [
                    emptyUser,
                ],
                createdAt: 0,
                startAt: 0,
                endAt: 0,
                ended: false,
                bingoCards: [
                    emptyBingoCard,
                ],
                unusedAmounts: {
                    steps: 1234,
                    activeMinutes: 5678,
                    distanceKm: 9012,
                }
            }
        }
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("1234")).toBeInTheDocument();
    expect(await screen.findByText("5678")).toBeInTheDocument();
    expect(await screen.findByText("9012")).toBeInTheDocument();
});

it('should render a card with a tile', async () => {
    const mock = mockFetchBingoQuery({
        data: {
            bingoChallenge: {
                id: 1,
                users: [
                    emptyUser,
                ],
                createdAt: 0,
                startAt: 0,
                endAt: 0,
                ended: false,
                bingoCards: [
                    {
                        ...emptyBingoCard,
                        tiles: [
                            {
                                ...emptyBingoTile,
                                steps: 1234
                            }
                        ]
                    },
                ],
                unusedAmounts: {
                    steps: 0,
                    activeMinutes: 0,
                    distanceKm: 0,
                }
            }
        }
    })

    render(
        <MockedProvider mocks={[mock]}>
            <BingoChallenge id={1} currentUser={emptyUser} />
        </MockedProvider>,
    );
    expect(await screen.findByText("1234")).toBeInTheDocument();
});
