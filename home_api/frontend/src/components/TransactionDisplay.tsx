import React, {useState} from 'react';
import _ from 'lodash';
import { createBrowserHistory } from "history";

import TransactionFilters from './TransactionFilters';
import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

function updateStateInUrl(param: string, stateFn: Function): Function {
    const history = createBrowserHistory();
    const query = new URLSearchParams(history.location.search)
    function update(value: any) {
        if (Array.isArray(value)) {
            query.set(param, value.join(','))
        } else {
            query.set(param, value);
        }
        history.replace({...history.location, search: query.toString()})
        stateFn(value);
    }
    return update;
}

function useStart(initialStart: string | null): [string, Function] {
    const defaultDate = new Date();
    const earliestDate = (defaultDate.getFullYear() - 1) + '-' + (defaultDate.getMonth() + 1) + '-' + defaultDate.getDate();
    const [start, setStart] = useState(initialStart || earliestDate);
    return [start, updateStateInUrl('start', setStart)];
}

function useEnd(initialEnd: string | null): [string, Function] {
    const defaultDate = new Date();
    const latestDate = defaultDate.getFullYear() + '-' + (defaultDate.getMonth() + 1) + '-' + defaultDate.getDate();
    const [end, setEnd] = useState(initialEnd || latestDate);
    return [end, updateStateInUrl('end', setEnd)];
}

function useMinAmount(initialMinAmount: number): [number, Function] {
    const [minAmount, setMinAmount] = useState(initialMinAmount);
    return [minAmount, updateStateInUrl('minAmount', setMinAmount)];
}

function useMaxAmount(initialMaxAmount: number): [number, Function] {
    const [maxAmount, setMaxAmount] = useState(initialMaxAmount);
    return [maxAmount, updateStateInUrl('maxAmount', setMaxAmount)];
}

function useTypes(initialTypes: string[]): [string[], Function] {
    const [types, setTypes] = useState(initialTypes);
    return [types, updateStateInUrl('types', setTypes)];
}

function useCategories(initialCategories: string[]): [string[], Function] {
    const [categories, setCategories] = useState(initialCategories);
    return [categories, updateStateInUrl('categories', setCategories)];
}

function useAccounts(initialAccounts: string[]): [string[], Function] {
    const [accounts, setAccounts] = useState(initialAccounts);
    return [accounts, updateStateInUrl('accounts', setAccounts)];
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

    const [minAmount, setMinAmount] = useMinAmount(parseInt(query.get('minAmount') || '0', 10));
    const [maxAmount, setMaxAmount] = useMaxAmount(parseInt(query.get('maxAmount') || '0', 10));

    const queryTypes = query.get('types');
    const defaultTypes = (queryTypes === null || queryTypes === '') ? [] : queryTypes.split(",")
    const [types, setTypes] = useTypes(defaultTypes);

    const queryCategories = query.get('categories')
    const defaultCategories = (queryCategories === null || queryCategories === '') ? [] : queryCategories.split(",")
    const [categories, setCategories] = useCategories(defaultCategories);

    const queryAccounts = query.get('accounts')
    const defaultAccounts = (queryAccounts === null || queryAccounts === '') ? [] : queryAccounts.split(",")
    const [accounts, setAccounts] = useAccounts(defaultAccounts);

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
        <div className="px-2">
            <div className="flex -mx-2">
                <div className="w-1/4 px-2">
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
                <div className="w-3/4 px-2">
                    {listElement}
                </div>
            </div>
        </div>
    );
}

export default TransactionDisplay;
