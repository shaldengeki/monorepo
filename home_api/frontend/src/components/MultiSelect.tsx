import React from 'react';
import _ from 'lodash';

type MultiSelectProps = {
    name: string,
    value: Array<string>,
    onChange: Function,
    allValues: Array<string>
}

const MultiSelect = ({name, value, onChange, allValues}: MultiSelectProps) => {
    const optionElement = (type: string, selectedValues: Array<string>) => {
        if (selectedValues.includes(type)) {
            return (<option value={type} selected>{type}</option>);
        } else {
            return (<option value={type}>{type}</option>);
        }
    }

    const getSelectedOptions = (options: HTMLOptionsCollection) => {
        return _.map(
            _.filter(options, (opt) => {return opt.selected;}),
            (opt) => { return opt.value; }
        );
    }

    return (
        <select
            multiple={true}
            name={name}
            value={value}
            onChange={(e) => {onChange(getSelectedOptions(e.target.options));}}
        >
            {_.map(
                allValues,
                (x) => {return optionElement(x, allValues);}
            )}
        </select>
    );
}
export default MultiSelect;
