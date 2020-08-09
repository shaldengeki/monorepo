import React, {useState} from 'react';
import _ from 'lodash';

import DatePicker from './DatePicker';
import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    const latestDate = Math.round(Date.now() / 1000 | 0);
    const earliestDate = latestDate - (365 * 24 * 60 * 60);

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