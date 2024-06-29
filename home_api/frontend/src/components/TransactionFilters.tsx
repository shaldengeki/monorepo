import React from 'react';
import _ from 'lodash';
import { gql } from '@apollo/client/core';
import { useQuery } from '@apollo/client/react/hooks';

import DatePicker from './DatePicker';
import MultiSelect from './MultiSelect';

const GET_FILTERS = gql`
    query TransactionFilters {
        amountRange {
            min
            max
        }
        accounts
        categories
        types
        dateRange {
            start
            end
        }
    }
`;

type TransactionFiltersProps = {
    start: string,
    onChangeStart: Function,
    end: string,
    onChangeEnd: Function,
    minAmount: number,
    onChangeMinAmount: Function,
    maxAmount: number,
    onChangeMaxAmount: Function,
    types: string[],
    onChangeTypes: Function,
    categories: string[],
    onChangeCategories: Function,
    accounts: string[],
    onChangeAccounts: Function,
}

const TransactionFilters = ({
    start,
    onChangeStart,
    end,
    onChangeEnd,
    minAmount,
    onChangeMinAmount,
    maxAmount,
    onChangeMaxAmount,
    types,
    onChangeTypes,
    categories,
    onChangeCategories,
    accounts,
    onChangeAccounts
}: TransactionFiltersProps) => {
    const { data, loading, error } = useQuery(GET_FILTERS);

    const loadingDisplay = <h1>Loading filters...</h1>;
    const errorDisplay = <h1>Error loading filters!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    return (
        <div>
            <DatePicker
                start={start}
                end={end}
                onChangeStart={onChangeStart}
                onChangeEnd={onChangeEnd}
            />
            <div className="mb-6">
                <label className="block mb-2" htmlFor="minAmount">Minimum Amount</label>
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    id="minAmount"
                    type="number"
                    placeholder="$0.00"
                    value={minAmount}
                    onChange={(e) => {onChangeMinAmount(e.target.value)}}
                />
            </div>
            <div className="mb-6">
                <label className="block mb-2" htmlFor="maxAmount">Maximum Amount</label>
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    id="maxAmount"
                    type="number"
                    placeholder="$0.00"
                    value={maxAmount}
                    onChange={(e) => {onChangeMaxAmount(e.target.value)}}
                />
            </div>
            <div className="mb-6">
                <label className="block mb-2" htmlFor="types">Types</label>
                <MultiSelect
                    name="types"
                    value={types}
                    onChange={onChangeTypes}
                    allValues={data.types}
                />
            </div>
            <div className="mb-6">
                <label className="block mb-2" htmlFor="types">Accounts</label>
                <MultiSelect
                    name="accounts"
                    value={accounts}
                    onChange={onChangeAccounts}
                    allValues={data.accounts}
                />
            </div>
            <div className="mb-6">
                <label className="block mb-2" htmlFor="types">Categories</label>
                <MultiSelect
                    name="categories"
                    value={categories}
                    onChange={onChangeCategories}
                    allValues={data.categories}
                />
            </div>
        </div>
    )
}
export default TransactionFilters;
