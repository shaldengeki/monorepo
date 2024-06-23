import React from 'react';
import _ from 'lodash';

const MultiSelect = (props) => {
    const {
        name,
        value,
        onChange,
        allValues
    } = props;

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

    return (
        <select
            multiple={true}
            name={name}
            value={value}
            onChange={(e) => {onChange(getSelectedOptions(e.target));}}
        >
            {_.map(
                allValues,
                (x) => {return optionElement(x, allValues);}
            )}
        </select>
    );
}
export default MultiSelect;

