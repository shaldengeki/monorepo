import React from 'react';

import DatePicker from './DatePicker';

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
        </div>
    )
}
export default TransactionFilters;

