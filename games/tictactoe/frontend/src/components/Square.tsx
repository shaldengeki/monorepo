import React, {PropsWithChildren} from 'react';

type SquareProps = {
    value: string;
    onSquareClick: React.MouseEventHandler<HTMLButtonElement>;
}

const Square = (props: PropsWithChildren<SquareProps>) => {
    return (
        <button className="square" onClick={props.onSquareClick}>
            {props.value}
        </button>
    );
}

export default Square;
