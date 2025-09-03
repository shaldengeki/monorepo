import {PropsWithChildren} from 'react';
import Square from './Square';

type BoardProps = {
    xIsNext: boolean;
    squares: Array<string>;
    onPlay: Function;
    className?: string;
}

const Board = (props: PropsWithChildren<BoardProps>) => {
    function handleClick(i: number) {
        if (props.squares[i] !== "" || calculateWinner(props.squares)) {
            return;
        }

        const nextSquares = props.squares.slice();
        if (props.xIsNext) {
            nextSquares[i] = "X";
        } else {
            nextSquares[i] = "O";
        }

        props.onPlay(nextSquares);
    }

    const winner = calculateWinner(props.squares);
    let status;
    if (winner) {
        status = "Winner: " + winner;
    } else {
        status = "Next player: " + (props.xIsNext ? "X" : "O");
    }

    return <>
    <div className="status">{status}</div>
        <div className="board-row">
            <Square value={props.squares[0]} onSquareClick={() => {handleClick(0)}} />
            <Square value={props.squares[1]} onSquareClick={() => {handleClick(1)}} />
            <Square value={props.squares[2]} onSquareClick={() => {handleClick(2)}} />
        </div>
        <div className="board-row">
            <Square value={props.squares[3]} onSquareClick={() => {handleClick(3)}} />
            <Square value={props.squares[4]} onSquareClick={() => {handleClick(4)}} />
            <Square value={props.squares[5]} onSquareClick={() => {handleClick(5)}} />
        </div>
        <div className="board-row">
            <Square value={props.squares[6]} onSquareClick={() => {handleClick(6)}} />
            <Square value={props.squares[7]} onSquareClick={() => {handleClick(7)}} />
            <Square value={props.squares[8]} onSquareClick={() => {handleClick(8)}} />
        </div>
    </>
};

const calculateWinner = (squares: Array<string>) => {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ];

    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i]
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a]
        }
    }

    return null;
}

export default Board;
