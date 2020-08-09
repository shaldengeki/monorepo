import React from 'react';

import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    const latestDate = Math.round(Date.now() / 1000 | 0);
    const earliestDate = latestDate - (365 * 24 * 60 * 60);

    return (
        <div>
            <TransactionChart earliestDate={earliestDate} latestDate={latestDate} />
            <TransactionList earliestDate={earliestDate} latestDate={latestDate} />
        </div>
    );
}

export default TransactionDisplay;
