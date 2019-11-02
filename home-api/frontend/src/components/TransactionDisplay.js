import React from 'react';

import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    return (
        <div>
            <TransactionChart />
            <TransactionList />
        </div>
    );
}

export default TransactionDisplay;