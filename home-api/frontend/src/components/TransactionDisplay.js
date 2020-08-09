import React from 'react';

import TransactionList from './TransactionList';
import TransactionChart from './TransactionChart';

const TransactionDisplay = () => {
    const latestDate = Math.round(Date.now() / 1000 | 0);
    const earliestDate = latestDate - (365 * 24 * 60 * 60);

    const [start, setStart] = useState(earliestDate);
    const [end, setEnd] = useState(latestDate);

    const parsedStart = Date.parse(start);
    const parsedEnd = Date.parse(end);

    const validDates = !(_.isNaN(start) || _.isNaN(end));

    const chartElement = validDates ? (<TransactionChart earliestDate={parsedStart} latestDate={parsedEnd} />) : (<div />);
    const listElement = validDates ? (<TransactionList earliestDate={parsedStart} latestDate={parsedEnd} />) : (<div />);

    return (
        <div>
            <DatePicker start={start} end={end} onChangeStart={setStart} onChangeEnd={setEnd} />
            {chartElement}
            {listElement}
        </div>
    );
}

export default TransactionDisplay;