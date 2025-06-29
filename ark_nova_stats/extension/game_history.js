var browser = (browser) ? browser : chrome;
const playerId = window.location.href.split('player=')[1].split('&')[0];
const playerName = document.getElementById("page_title").children[0].textContent;

const apiEndpoint = "https://api.arknova.ouguo.us/graphql";

function makeAPIRequest(body) {
    let apiHeaders = new Headers();
    apiHeaders.append("Content-Type", "application/json");

    let apiRequest = new Request(apiEndpoint, {
      method: "POST",
      headers: apiHeaders,
      body: body,
      mode: "no-cors",
    });

    return fetch(apiRequest);
}

console.log("Player ID: ", playerId);
console.log("Player name: ", playerName);

const syncGame = async (tableId, gameEntryRow) => {
    gameEntryRow.style.opacity = 0.4;
    console.log("Syncing table ID", tableId);
    const promise = makeAPIRequest(
        JSON.stringify({
            query: "query FetchGameLog($tableId: Int!) {\n  gameLog(id: $tableId) {\n    bgaTableId\n  }\n}",
            variables: {
                tableId
            },
            operationName: "FetchGameLog",
        })
    ).then((resp) => {
        console.log("Response", resp);
        gameEntryRow.style.opacity = 1;

    }, (resp) => {
        console.log("Response", resp);
        gameEntryRow.style.opacity = 1;
    })

    return promise
}

const syncGames = async (event) => {
    console.log("Syncing games...");
    const gameHistoryTable = document.getElementById("gamelist_inner");

    const gamePromises = [];

    for (const gameEntryRow of gameHistoryTable.children) {
        const links = gameEntryRow.getElementsByTagName("a");
        let tableLink = null;
        for (var link of links) {
            if (link.textContent === "Ark Nova") {
                tableLink = link;
                break;
            }
        }
        const tableId = tableLink.href.split("table=")[1];
        console.log("Table ID", tableId);

        const ranks = gameEntryRow.getElementsByClassName("rank");
        let ranksPresent = true;
        for (const rank of ranks) {
            ranksPresent = ranksPresent && (rank.textContent !== "-");
        }

        if (!ranksPresent) {
            console.log("Ranks not present for table " + tableId + ", skipping.");
            continue;
        }

        gamePromises.push(syncGame(tableId, gameEntryRow));
    }

    return await Promise.all(gamePromises);
}

const addSyncLinkToGameHistoryHeader = () => {
    const titles = document.getElementsByClassName("pagesection__title");
    let gameHistoryHeader = null;
    for (var titleElt of titles) {
        if (titleElt.textContent === "Games history") {
            gameHistoryHeader = titleElt;
        }
    }

    if (gameHistoryHeader === null) {
        console.log("Couldn't find game history element; bailing early.");
        return;
    }

    const syncLink = document.createElement("a");
    syncLink.className = "bga-link smalltext";
    syncLink.append("(sync w/db)");
    syncLink.addEventListener("click", syncGames);
    gameHistoryHeader.append(syncLink);
}

addSyncLinkToGameHistoryHeader();
