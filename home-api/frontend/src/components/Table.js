import React, {useState} from 'react';
import _ from 'lodash';

const renderColumn = (col, idx, filters, setFilter, tablePrefix) => {
    return (
        <th key={`${tablePrefix}-col-${idx}`} className="px-4 py-2">
            <p>{_.startCase(col)}</p>
            <input
                className="border"
                type="text"
                name="filter[{}]"
                value={filters[col]}
                onChange={e => setFilter(col, e.target.value)}
            />
        </th>
    )
}

const useColumnFilters = (cols) => {
    const defaultFilters = _.fromPairs(_.map(cols, (c) => { return [c, '']; }));
    const [filters, setFilters] = useState(defaultFilters);
    function setFilter(name, value) {
        const newFilters = _.clone(filters)
        newFilters[name] = value;
        setFilters(newFilters);
    }
    return [filters, setFilter];
}

const renderRow = (row, idx, cols, tablePrefix) => {
    let rowPrefix = `${tablePrefix}-row-${idx}`;
    return (
        <tr key={rowPrefix}>
            {cols.map((col, colIdx) => {
                return <td key={`${rowPrefix}-col-${colIdx}`} className="border px-4 py-2">{row[col]}</td>;
            })}
        </tr>
    );
}

const Table = (props) => {
    const {cols, rows, keyPrefix} = props;
    const [filters, setFilter] = useColumnFilters(cols);
    const tablePrefix = `Table-${keyPrefix}`;

    let shownRows = rows || [];
    _.forEach(cols, (col) => {
        if (filters[col]) {
            shownRows = _.filter(shownRows, (txn) => { return _.upperCase(txn[col]).includes(_.upperCase(filters[col])); });
        }
    });

    return (
        <table key={tablePrefix} className="table-auto">
            <thead>
                <tr>
                    {cols.map((col, idx) => renderColumn(col, idx, filters, setFilter, tablePrefix))}
                </tr>
            </thead>
            <tbody>
                {shownRows.map((row, idx) => renderRow(row, idx, cols, tablePrefix))}
            </tbody>
        </table>
    );
}

export default Table;