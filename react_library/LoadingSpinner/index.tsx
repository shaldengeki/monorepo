import {PropsWithChildren} from 'react';

type LoadingSpinnerProps = {
    className?: string;
}

const LoadingSpinner = (props: PropsWithChildren<LoadingSpinnerProps>) => {
    const defaultClassNames = "";
    const actualClassNames = props.className ? defaultClassNames + " " + props.className : defaultClassNames;

    return (
        <div className={actualClassNames}>
            <p>Loading...</p>
            {props.children}
        </div>
    );
}

export default LoadingSpinner;
