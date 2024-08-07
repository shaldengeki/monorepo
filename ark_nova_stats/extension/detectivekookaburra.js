let pattern = "https://boardgamearena.com/*";
let apiEndpoint = "https://api.arknova.ouguo.us/graphql";

function handleRequest(requestDetails) {
  if (!requestDetails.url.includes("logs.html")) {
    return;
  }

  let filter = browser.webRequest.filterResponseData(requestDetails.requestId);
  let decoder = new TextDecoder("utf-8");
  let encoder = new TextEncoder();

  const data = [];

  filter.ondata = (event) => {
    data.push(event.data);
  }

  filter.onstop = (event) => {
    let str = "";
    let seenScoringEvent = false;

    // Decode all the pushed data and assemble a string representing the entire response.
    if (data.length === 1) {
      str = decoder.decode(data[0]);
    } else {
      for (let i = 0; i < data.length; i++) {
        const stream = i !== data.length - 1;
        const decodedChunk = decoder.decode(data[i], { stream });
        seenScoringEvent = seenScoringEvent || decodedChunk.includes("from the deck (scoring cards)");
        str += decodedChunk;
      }
    }

    if (!seenScoringEvent) {
      console.log("No scoring event seen, assuming this isn't an Ark Nova replay and skipping.");
      filter.write(encoder.encode(str));
      filter.disconnect();
      return {};
    }

    let apiHeaders = new Headers();
    apiHeaders.append("Content-Type", "application/json");

    let apiRequest = new Request(apiEndpoint, {
      method: "POST",
      headers: apiHeaders,
      body: JSON.stringify({
        query: "mutation SubmitGameLog($logs: String!) {\n  submitGameLogs(logs: $logs) {\n    id\n  }\n}",
        variables: {
          logs: str,
        },
        operationName: "SubmitGameLog",
      })
    });
    let apiPromise = fetch(apiRequest).then(
      data => {
        console.log(`Made API request: ${data.json()}`)
      }
    )

    filter.write(encoder.encode(str));
    filter.disconnect();

    return apiPromise;
  }

  return {};
}

browser.webRequest.onBeforeRequest.addListener(
  handleRequest,
  { urls: [pattern] },
  ["blocking"],
);
