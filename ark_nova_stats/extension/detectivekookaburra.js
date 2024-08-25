let pattern = "https://boardgamearena.com/*";
let apiEndpoint = "https://api.arknova.ouguo.us/graphql";

function readEntireResponse(data) {
  let str = "";
  let decoder = new TextDecoder("utf-8");

  // Decode all the pushed data and assemble a string representing the entire response.
  if (data.length === 1) {
    str = decoder.decode(data[0]);
  } else {
    for (let i = 0; i < data.length; i++) {
      const stream = i !== data.length - 1;
      const decodedChunk = decoder.decode(data[i], { stream });
      str += decodedChunk;
    }
  }

  return str;
}

function makeAPIRequest(body) {
  let apiHeaders = new Headers();
  apiHeaders.append("Content-Type", "application/json");

  let apiRequest = new Request(apiEndpoint, {
    method: "POST",
    headers: apiHeaders,
    body: body,
  });

  return fetch(apiRequest);
}

function handleLogsRequest(requestDetails) {
  let filter = browser.webRequest.filterResponseData(requestDetails.requestId);
  let encoder = new TextEncoder();

  const data = [];

  filter.ondata = (event) => {
    data.push(event.data);
  }

  filter.onstop = (event) => {
    const response = readEntireResponse(data);

    if (!response.includes("from the deck (scoring cards)")) {
      console.log("No scoring event seen, assuming this isn't an Ark Nova replay and skipping.");
      filter.write(encoder.encode(response));
      filter.disconnect();
      return {};
    }

    const apiPromise = makeAPIRequest(
      JSON.stringify({
        query: "mutation SubmitGameLog($logs: String!) {\n  submitGameLogs(logs: $logs) {\n    id\n  }\n}",
        variables: {
          logs: response,
        },
        operationName: "SubmitGameLog",
      })
    ).then(
      data => {
        console.log(`Made game logs API request: ${data.json()}`)
      }
    );

    filter.write(encoder.encode(response));
    filter.disconnect();

    return apiPromise;
  }

  return {};
}

function handleRatingsRequest(requestDetails) {
  const url = new URL(requestDetails.url);
  const tableId = parseInt(url.searchParams.get("id"), 10);

  if (tableId === null) {
    console.log("No table ID found in URL, bailing.");
    return {}
  }

  let filter = browser.webRequest.filterResponseData(requestDetails.requestId);
  let encoder = new TextEncoder();

  const data = [];

  filter.ondata = (event) => {
    data.push(event.data);
  }

  filter.onstop = (event) => {
    const response = readEntireResponse(data);

    const apiPromise = makeAPIRequest(
      JSON.stringify({
        query: "mutation SubmitGameRatings($ratings:String!,$tableId:Int!) {\n  submitGameRatings(ratings:$ratings,tableId:$tableId) {\n    id\n  }\n}",
        variables: {
          ratings: response,
          tableId: tableId,
        },
        operationName: "SubmitGameRatings",
      })
    ).then(
      data => {
        console.log(`Made game ratings API request: ${data.json()}`)
      }
    );

    filter.write(encoder.encode(response));
    filter.disconnect();

    return apiPromise;
  }

  return {};
}

function handleRequest(requestDetails) {
  if (requestDetails.url.includes("logs.html")) {
    return handleLogsRequest(requestDetails);
  } else if (requestDetails.url.includes("tableratingsupdate.html")) {
    return handleRatingsRequest(requestDetails);
  }
}

browser.webRequest.onBeforeRequest.addListener(
  handleRequest,
  { urls: [pattern] },
  ["blocking"],
);
