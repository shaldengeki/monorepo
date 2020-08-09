import React, {useState} from 'react';
import _ from 'lodash';

import DatePicker from './DatePicker';
import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    const defaultDate = new Date();
    const latestDate = defaultDate.getFullYear() + '-' + defaultDate.getMonth() + '-' + defaultDate.getDay();
    const earliestDate = (defaultDate.getFullYear() - 1) + '-' + defaultDate.getMonth() + '-' + defaultDate.getDay();

    const [start, setStart] = useState(earliestDate);
    const [end, setEnd] = useState(latestDate);

    const parsedStart = Date.parse(start);
    const parsedEnd = Date.parse(end);

    const validDates = !(_.isNaN(parsedStart) || _.isNaN(parsedEnd));

    const parsedStartSeconds = Math.round(parsedStart / 1000);
    const parsedEndSeconds = Math.round(parsedEnd / 1000);

    const chartElement = validDates ? (<TransactionChart earliestDate={parsedStartSeconds} latestDate={parsedEndSeconds} />) : (<div />);
    const listElement = validDates ? (<TransactionList earliestDate={parsedStartSeconds} latestDate={parsedEndSeconds} />) : (<div />);

    return (
        <div>
            <DatePicker start={start} end={end} onChangeStart={setStart} onChangeEnd={setEnd} />
            {chartElement}
            {listElement}
        </div>
    );
}

export default TransactionDisplay;
