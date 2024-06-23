import React from 'react';

const DatePicker = (props) => {
    const {start, end, onChangeStart, onChangeEnd} = props;
    return (
        <div>
            <div>
                <p>Start</p>
                <input
                    className="border"
                    type="text"
                    name="start"
                    value={start}
                    onChange={(e) => {onChangeStart(e.target.value)}}
                />
            </div>
            <div>
                <p>End</p>
                <input
                    className="border"
                    type="text"
                    name="end"
                    value={end}
                    onChange={(e) => {onChangeEnd(e.target.value)}}
                />
            </div>
        </div>
    );
}

export default DatePicker;