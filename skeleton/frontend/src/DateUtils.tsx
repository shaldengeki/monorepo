export function getCurrentUnixTime(): number {
    const currentTime = Date.now();
    return Math.round(currentTime / 1000);
}

export function formatDateDifference(seconds: number): string {
    let unit = "";
    let quantity = 0;
    if (seconds === 0) {
        unit = "seconds";
        quantity = seconds;
    } else if (seconds < 60) {
        unit = "second";
        quantity = seconds;
    } else if (seconds < 3600) {
        quantity = Math.floor(seconds / 60);
        unit = "minute";
    } else if (seconds < 86400) {
        quantity = Math.floor(seconds / 3600);
        unit = "hour";
    } else if (seconds < 604800) {
        quantity = Math.floor(seconds / 86400);
        unit = "day";
    } else if (seconds < 2592000) {
        quantity = Math.floor(seconds / 604800);
        unit = "week";
    } else if (seconds < 31536000) {
        quantity = Math.floor(seconds / 2592000);
        unit = "month";
    } else {
        quantity = Math.floor(seconds / 31536000);
        unit = "year";
    }

    if (quantity > 1) {
        unit = unit + "s";
    }

    return quantity + " " + unit;
}

export function today(): number {
    let d = new Date();
    d.setHours(0);
    d.setMinutes(0);
    d.setSeconds(0);
    d.setMilliseconds(0);
    return d.getTime() / 1000;
}

export function nextMonday(): number {
    let d = new Date();
    d.setDate(d.getDate() + (1 + 7 - d.getDay()) % 7);
    d.setHours(0);
    d.setMinutes(0);
    d.setSeconds(0);
    d.setMilliseconds(0);
    return d.getTime() / 1000;
}

export function nextSaturday(): number {
    let d = new Date();
    d.setDate(d.getDate() + (6 + 7 - d.getDay()) % 7);
    d.setHours(0);
    d.setMinutes(0);
    d.setSeconds(0);
    d.setMilliseconds(0);
    return d.getTime() / 1000;
}

export function padDate(date: number): string {
    let formattedDate = "" + date;
    if (date < 10) {
        formattedDate = "0" + formattedDate;
    }
    return formattedDate;
}

export function getDate(time?: number): string {
    let currTime = new Date();
    if (time !== undefined) {
        currTime = new Date(0);
        currTime.setUTCSeconds(time);
    }
    const formattedMonth = padDate(currTime.getMonth() + 1);
    const formattedDate = padDate(currTime.getDate());

    return currTime.getFullYear() + "-" + (formattedMonth) + "-" + formattedDate;
}

export function convertDateStringToEpochTime(dateString: string): number {
    return new Date(dateString + "T00:00:00").getTime() / 1000;
}
