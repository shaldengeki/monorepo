import React, {useState} from 'react';
import _ from 'lodash';
import { createBrowserHistory } from "history";

import TransactionFilters from './TransactionFilters';
import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

function useStart(initialStart) {
    const history = createBrowserHistory();
    const query = new URLSearchParams(history.location.search)
    const defaultDate = new Date();
    const earliestDate = (defaultDate.getFullYear() - 1) + '-' + defaultDate.getMonth() + '-' + defaultDate.getDate();
    const [start, setStart] = useState(initialStart || earliestDate);

    function updateStart(value) {
        query.set('start', value);
        history.replace({...history.location, search: query.toString()})
        setStart(value);
    }

    return [start, updateStart];
}

function useEnd(initialEnd) {
    const history = createBrowserHistory();
    const query = new URLSearchParams(history.location.search)
    const defaultDate = new Date();
    const latestDate = defaultDate.getFullYear() + '-' + defaultDate.getMonth() + '-' + defaultDate.getDate();
    const [end, setEnd] = useState(initialEnd || latestDate);

    function updateEnd(value) {
        query.set('end', value);
        history.replace({...history.location, search: query.toString()})
        setEnd(value);
    }

    return [end, updateEnd];
}

const TransactionDisplay = () => {

    const history = createBrowserHistory();
    const query = new URLSearchParams(history.location.search)

    const [start, setStart] = useStart(query.get('start'));
    const [end, setEnd] = useEnd(query.get('end'));

    const parsedStart = Date.parse(start);
    const parsedEnd = Date.parse(end);
    const validDates = !(_.isNaN(parsedStart) || _.isNaN(parsedEnd));
    const parsedStartSeconds = Math.round(parsedStart / 1000);
    const parsedEndSeconds = Math.round(parsedEnd / 1000);

    const [minAmount, setMinAmount] = useState(parseInt(query.get('minAmount'), 10) || 0);
    const [maxAmount, setMaxAmount] = useState(parseInt(query.get('maxAmount'), 10) || 1000000);

    const defaultTypes = (query.get('types') === null) ? [] : query.get('types').split(",")
    const [types, setTypes] = useState(defaultTypes);

    const defaultCategories = (query.get('categories') === null) ? [] : query.get('categories').split(",")
    const [categories, setCategories] = useState(defaultCategories);

    const defaultAccounts = (query.get('accounts') === null) ? [] : query.get('accounts').split(",")
    const [accounts, setAccounts] = useState(defaultAccounts);

    const chartElement = validDates ? (
        <TransactionChart
            earliestDate={parsedStartSeconds}
            latestDate={parsedEndSeconds}
            minAmount={minAmount*100}
            maxAmount={maxAmount*100}
            types={types}
            categories={categories}
            accounts={accounts}
        />
    ) : (<div />);
    const listElement = validDates ? (
        <TransactionList
            earliestDate={parsedStartSeconds}
            latestDate={parsedEndSeconds}
            minAmount={minAmount*100}
            maxAmount={maxAmount*100}
            types={types}
            categories={categories}
            accounts={accounts}
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
