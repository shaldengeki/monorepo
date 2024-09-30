import React, { useState } from 'react'
import _ from 'lodash'

const renderColumn = (col: string, showFilters: Boolean | undefined, filters: _.Dictionary<any>, setFilter: Function, tablePrefix: string) => {
  const filterInput = (
    <input
      className="border w-full"
      type="text"
      name="filter[{}]"
      value={filters[col]}
      onChange={e => setFilter(col, e.target.value)}
    />
  )

  return (
        <th key={`${tablePrefix}-col-${col}`} className="px-4 py-2">
            <p>{_.startCase(col)}</p>
            {showFilters ? filterInput : ''}
        </th>
  )
}

const useColumnFilters = (cols: string[]): [any, Function] => {
  const defaultFilters = _.fromPairs(_.map(cols, (c) => { return [c, ''] }))
  const [filters, setFilters] = useState(defaultFilters)
  function setFilter (name: string, value: string) {
    const newFilters = _.clone(filters)
    newFilters[name] = value
    setFilters(newFilters)
  }
  return [filters, setFilter]
}

const renderRow = (row: any, idx: number, cols: Array<string>, tablePrefix: string) => {
  const rowPrefix = (row.id === undefined) ? `${tablePrefix}-row-${idx}` : `${tablePrefix}-row-${row.id}`
  return (
        <tr key={rowPrefix}>
            {cols.map((col) => {
              return <td key={`${rowPrefix}-col-${col}`} className="border px-4 py-2">{row[col]}</td>
            })}
        </tr>
  )
}

interface TableRow {
  [index: string]:React.JSX.Element;
}

interface TableProps<T extends TableRow> {
  key: string;
  rows: Array<T>;
  showFilters?: Boolean;
}

function Table<T extends TableRow>({ key, rows, showFilters }: TableProps<T>) {
  const cols = Object.keys(rows[0]);

  const [filters, setFilter] = useColumnFilters(cols)
  const tablePrefix = `Table-${key}`

  let shownRows = rows || []
  if (showFilters) {
    _.forEach(cols, (col) => {
      if (filters[col]) {
        shownRows = _.filter(shownRows, (row: T) => {
          return _.upperCase(row[col].props.children).includes(_.upperCase(filters[col]))
        })
      }
    })
  }

  return (
        <table key={tablePrefix} className="w-full table-fixed text-center">
            <thead>
                <tr>
                    {cols.map(col => renderColumn(col, showFilters, filters, setFilter, tablePrefix))}
                </tr>
            </thead>
            <tbody>
                {shownRows.map((row, idx) => renderRow(row, idx, cols, tablePrefix))}
            </tbody>
        </table>
  )
}

export default Table
