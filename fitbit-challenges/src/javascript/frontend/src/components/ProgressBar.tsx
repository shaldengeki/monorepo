import * as React from 'react';

type ProgressBarProps = {
    value: number;
    maximum: number;
}

const ProgressBar = ({ value, maximum }: ProgressBarProps) => {
    const inversePercent = (maximum === 0) ? 100 : 100 - (100 * value / maximum);
    const barStyles = {
        "width": `${inversePercent}%`
    };
    return (
        <div className="mb-6 h-7 w-full text-right bg-gradient-to-r bg-teal-400 dark:from-indigo-500 dark:via-purple-500 dark:to-pink-500">
            <div
                className="h-7 bg-neutral-200 dark:bg-neutral-800 dark:text-slate-200"
                style={barStyles}
            >
                &nbsp;{value.toLocaleString()}&nbsp;
            </div>
        </div>
    );
};

export default ProgressBar;
