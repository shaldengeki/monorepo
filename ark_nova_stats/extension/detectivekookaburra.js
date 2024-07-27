let pattern = "https://boardgamearena.com/*";
let apiEndpoint = "https://api.arknova.ouguo.us/graphql";

function handleRequest(requestDetails) {
  console.log(`Handling: ${requestDetails.url}`);
  if (!requestDetails.url.includes("logs.html")) {
    console.log("Not logs.html, skipping");
    return;
  }

  let filter = browser.webRequest.filterResponseData(requestDetails.requestId);
  let decoder = new TextDecoder("utf-8");
  let encoder = new TextEncoder();

  filter.ondata = event => {
    let str = decoder.decode(event.data, {stream: true});
    console.log("Received data", str);

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
