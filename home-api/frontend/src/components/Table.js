import React, {useState} from 'react';
import _ from 'lodash';

const renderColumn = (col, filters, setFilter) => {
    return (
        <th class="px-4 py-2">
            <p>{_.startCase(col)}</p>
            <input
                class="border"
                type="text"
                name="filter[{}]"
                value={filters[col]}
                onChange={e => setFilter(col, e.target.value)}
            />
        </th>
    )
}

function useColumnFilters(cols) {
    const defaultFilters = _.fromPairs(_.map(cols, (c) => { return [c, '']; }));
    const [filters, setFilters] = useState(defaultFilters);
    function setFilter(name, value) {
        const newFilters = _.clone(filters)
        newFilters[name] = value;
        setFilters(newFilters);
    }
    return [filters, setFilter];
}

const renderRow = (row, cols) => {
    return (
        <tr>
            {cols.map(col => {
                return <td class="border px-4 py-2">{row[col]}</td>;
            })}
        </tr>
    );
}

const Table = (props) => {
    const {cols, rows, renderRow} = props;
    const [filters, setFilter] = useColumnFilters(cols);

    let shownRows = rows || [];
    _.forEach(cols, (col) => {
        if (filters[col]) {
            shownRows = _.filter(shownRows, (txn) => { return _.upperCase(txn[col]).includes(_.upperCase(filters[col])); });
        }
    });

    return (
        <table class="table-auto">
            <thead>
                <tr>
                    {cols.map(col => renderColumn(col, filters, setFilter))}
                </tr>
            </thead>
            <tbody>
                {shownRows.map(txn => renderRow(txn, cols))}
            </tbody>
        </table>
    );
}

export default Table;