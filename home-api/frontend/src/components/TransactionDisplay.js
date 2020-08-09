import React, {useState} from 'react';
import _ from 'lodash';

import TransactionFilters from './TransactionFilters';
import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    const defaultDate = new Date();
    const latestDate = defaultDate.getFullYear() + '-' + defaultDate.getMonth() + '-' + defaultDate.getDate();
    const earliestDate = (defaultDate.getFullYear() - 1) + '-' + defaultDate.getMonth() + '-' + defaultDate.getDate();

    const [start, setStart] = useState(earliestDate);
    const [end, setEnd] = useState(latestDate);
    const [minAmount, setMinAmount] = useState(0);
    const [maxAmount, setMaxAmount] = useState(1000000);
    const [types, setTypes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [accounts, setAccounts] = useState([]);

    const parsedStart = Date.parse(start);
    const parsedEnd = Date.parse(end);

    const validDates = !(_.isNaN(parsedStart) || _.isNaN(parsedEnd));

    const parsedStartSeconds = Math.round(parsedStart / 1000);
    const parsedEndSeconds = Math.round(parsedEnd / 1000);

    const chartElement = validDates ? (
        <TransactionChart
            earliestDate={parsedStartSeconds}
            latestDate={parsedEndSeconds}
            minAmount={minAmount*100}
            maxAmount={maxAmount*100}
        />
    ) : (<div />);
    const listElement = validDates ? (
        <TransactionList
            earliestDate={parsedStartSeconds}
            latestDate={parsedEndSeconds}
            minAmount={minAmount*100}
            maxAmount={maxAmount*100}
        />
    ) : (<div />);

    return (
        <div class="px-2">
            <div class="flex -mx-2">
                <div class="w-1/4 px-2">
                    <TransactionFilters
                        start={start}
                        onChangeStart={setStart}
                        end={end}
                        onChangeEnd={setEnd}
                        minAmount={minAmount}
                        onChangeMinAmount={setMinAmount}
                        maxAmount={maxAmount}
                        onChangeMaxAmount={setMaxAmount}
                        types={types}
                        onChangeTypes={setTypes}
                        categories={categories}
                        onChangeCategories={setCategories}
                        accounts={accounts}
                        onChangeAccounts={setAccounts}
                    />
                    {chartElement}
                </div>
                <div class="w-3/4 px-2">
                    {listElement}
                </div>
            </div>
        </div>
    );
}

export default TransactionDisplay;
