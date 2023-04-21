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
        <div className="mb-6 h-7 w-full bg-teal-400 dark:bg-pink-900 text-right">
            <div className="h-7 bg-neutral-200 dark:bg-neutral-600 dark:text-slate-400" style={barStyles}>
                {value}
            </div>
        </div>
    );
};

export default ProgressBar;
