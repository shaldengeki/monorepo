import React from 'react';
import _ from 'lodash';
import gql from "graphql-tag";
import { useQuery } from '@apollo/react-hooks';

import DatePicker from './DatePicker';

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

const TransactionFilters = (props) => {
    const {
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
    } = props;

    const { data, loading, error } = useQuery(GET_FILTERS);

    const loadingDisplay = <h1>Loading filters...</h1>;
    const errorDisplay = <h1>Error loading filters!</h1>;

    if (loading) return loadingDisplay;
    if (error) return errorDisplay;

    const optionElement = (type, selectedValues) => {
        if (selectedValues.includes(type)) {
            return (<option value={type} selected>{type}</option>);
        } else {
            return (<option value={type}>{type}</option>);
        }
    }

    const getSelectedOptions = (select) => {
        return _.map(
            _.filter(select.options, (opt) => {return opt.selected;}),
            (opt) => { return opt.value; }
        );
    }

    console.log("TransactionFilters types", types);

    const typesElement = (
        <select
            multiple={true}
            name="types"
            value={types}
            onChange={(e) => {
                const selectedOptions = getSelectedOptions(e.target);
                console.log('typesElement change', e.target, 'selectedOptions', selectedOptions);
                onChangeTypes(selectedOptions);
            }}>
            {_.map(
                data.types,
                (type) => {return optionElement(type, types);}
            )}
        </select>
    );

    const categoriesElement = (
        <select multiple={true} name="categories" value={categories} onChange={(e) => {onChangeCategories(e.target.value)}}>
            {_.map(
                data.categories,
                (category) => {return optionElement(category, categories);}
            )}
        </select>
    );

    const accountsElement = (
        <select multiple={true} name="accounts" value={accounts} onChange={(e) => {onChangeAccounts(e.target.value)}}>
            {_.map(
                data.accounts,
                (account) => {return optionElement(account, accounts);}
            )}
        </select>
    );

    return (
        <div>
            <DatePicker
                start={start}
                end={end}
                onChangeStart={onChangeStart}
                onChangeEnd={onChangeEnd}
            />
            <div class="mb-6">
                <label class="block mb-2" for="minAmount">Minimum Amount</label>
                <input
                    class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    id="minAmount"
                    type="number"
                    placeholder="$0.00"
                    value={minAmount}
                    onChange={(e) => {onChangeMinAmount(e.target.value)}}
                />
            </div>
            <div class="mb-6">
                <label class="block mb-2" for="maxAmount">Maximum Amount</label>
                <input
                    class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    id="maxAmount"
                    type="number"
                    placeholder="$0.00"
                    value={maxAmount}
                    onChange={(e) => {onChangeMaxAmount(e.target.value)}}
                />
            </div>
            <div class="mb-6">
                <label class="block mb-2" for="types">Types</label>
                {typesElement}
            </div>
            <div class="mb-6">
                <label class="block mb-2" for="types">Accounts</label>
                {accountsElement}
            </div>
            <div class="mb-6">
                <label class="block mb-2" for="types">Categories</label>
                {categoriesElement}
            </div>
        </div>
    )
}
export default TransactionFilters;

