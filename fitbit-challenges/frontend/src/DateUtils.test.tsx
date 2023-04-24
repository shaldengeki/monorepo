import { formatDateDifference } from './DateUtils';

it ('should keep a singular second', async() => {
    expect(formatDateDifference(1)).toBe("1 second");
})

it ('should pluralize multiple seconds', async() => {
    expect(formatDateDifference(23)).toBe("23 seconds");
})

it ('should convert to minutes', async() => {
    expect(formatDateDifference(60)).toBe("1 minute");
})

it ('should truncate to minutes', async() => {
    expect(formatDateDifference(119)).toBe("1 minute");
})

it ('should convert to hours', async() => {
    expect(formatDateDifference(3600)).toBe("1 hour");
})

it ('should convert to days', async() => {
    expect(formatDateDifference(86400)).toBe("1 day");
})

it ('should convert to weeks', async() => {
    expect(formatDateDifference(604800)).toBe("1 week");
})

it ('should convert to months', async() => {
    expect(formatDateDifference(2592000)).toBe("1 month");
})

it ('should convert to years', async() => {
    expect(formatDateDifference(31536000)).toBe("1 year");
})

it ('should handle multiple years', async() => {
    expect(formatDateDifference(95718330)).toBe("3 years");
})
