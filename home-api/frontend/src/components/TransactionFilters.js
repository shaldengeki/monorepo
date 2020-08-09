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
        <DatePicker
            start={start}
            end={end}
            onChangeStart={onChangeStart}
            onChangeEnd={onChangeEnd}
        />
    )
}
export default TransactionFilters;

