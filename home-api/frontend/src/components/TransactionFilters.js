import React from 'react';

import DatePicker from './DatePicker';

const TransactionFilters = (props) => {
    const {
        start,
        setStart,
        end,
        setEnd,
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
        <DatePicker
            start={start}
            end={end}
            onChangeStart={setStart}
            onChangeEnd={setEnd}
        />
    )
}
export default TransactionFilters;

