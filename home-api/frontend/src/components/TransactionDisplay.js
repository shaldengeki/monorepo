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
        <div class="px-2">
            <div class="flex -mx-2">
                <div class="w-1/4 px-2">
                    <DatePicker start={start} end={end} onChangeStart={setStart} onChangeEnd={setEnd} />
                </div>
                <div class="w-1/2 px-2">
                    {listElement}
                </div>
                <div class="w-1/4 px-2">
                    {chartElement}
                </div>
            </div>
        </div>
    );
}

export default TransactionDisplay;
