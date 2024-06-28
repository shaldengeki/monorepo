import { render } from '@testing-library/react';
import DatePicker from './DatePicker';
import React from 'react';

it('should render', async () => {
    render(
        <DatePicker start={"2024-06-01"} end={"2024-06-10"} onChangeStart={() => {}} onChangeEnd={() => {}} />
    );
});
