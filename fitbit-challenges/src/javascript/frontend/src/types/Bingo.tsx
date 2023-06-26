import User, {emptyUser} from './User'

export type BingoTile = {
    id: number
    steps: number | null
    activeMinutes: number | null
    distanceKm: number | null
    coordinateX: number
    coordinateY: number
    flipped: boolean
    requiredForWin: boolean
}

export const emptyBingoTile: BingoTile = {
    id: 0,
    steps: null,
    activeMinutes: null,
    distanceKm: null,
    coordinateX: 0,
    coordinateY: 0,
    flipped: false,
    requiredForWin: false
}

type BingoCard = {
    user: User
    rows: number
    columns: number
    tiles: Array<BingoTile>
}

export const emptyBingoCard: BingoCard = {
    user: emptyUser,
    rows: 0,
    columns: 0,
    tiles: []
}

export default BingoCard;
