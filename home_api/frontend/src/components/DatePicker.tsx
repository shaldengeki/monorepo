import React from 'react';

type DatePickerProps = {
    start: number,
    end: number,
    onChangeStart: Function,
    onChangeEnd: Function
}

const DatePicker = ({start, end, onChangeStart, onChangeEnd}: DatePickerProps) => {
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
