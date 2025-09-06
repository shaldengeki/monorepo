import { gql } from '@apollo/client/core';

export const FETCH_CURRENT_USER_QUERY = gql`
    query FetchCurrentUser {
          currentUser {
            fitbitUserId
            displayName
            createdAt
          }
      }
`;

export const CREATE_USER_ACTIVITY_MUTATION = gql`
    mutation CreateUserActivity(
        $user:String!,
        $recordDate:Int!,
        $steps:Int!,
    ) {
        createUserActivity(
            recordDate:$recordDate,
            user:$user,
            steps:$steps,
            activeMinutes:0,
            distanceKm:0
        ) {
            id
            recordDate
            user
            steps
        }
    }
`

export const UPDATE_USER_ACTIVITY_MUTATION = gql`
    mutation UpdateUserActivity(
        $id:Int!,
        $user:String!,
        $recordDate:Int!,
        $steps:Int!,
    ) {
        updateUserActivity(
            id:$id,
            recordDate:$recordDate,
            user:$user,
            steps:$steps,
            activeMinutes:0,
            distanceKm:0
        ) {
            id
            recordDate
            user
            steps
        }
    }
`

export const FETCH_WORKWEEK_HUSTLE_QUERY = gql`
    query FetchChallenge($id: Int!) {
          challenges(id: $id) {
              id
              challengeType
              users {
                fitbitUserId
                displayName
              }
              createdAt
              startAt
              endAt
              ended
              sealAt
              sealed
              activities {
                id
                user
                createdAt
                recordDate
                steps
                activeMinutes
                distanceKm
              }
          }
          currentUser {
            fitbitUserId
            displayName
            createdAt
          }
      }
`;



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
