var browser = (browser) ? browser : chrome;

document.addEventListener('DOMContentLoaded', function () {
  const disablePlayersControl = document.getElementById('hidePlayers');
  const displayEloControl = document.getElementById('displayElo');
  const displayTimerControl = document.getElementById('displayTimer');
  const recordGameLog = document.getElementById('recordGameLog');

  browser.storage.sync.get('disablePlayers').then((result) => {
    const checked = result.disablePlayers || false;
    disablePlayersControl.checked = checked;

    // chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    //   chrome.scripting.executeScript({
    //     target: { tabId: tabs[0].id },
    //     function: () => {
    //       window.disablePlayers = checked;
    //     },
    //     args: [checked],
    //   });
    // });
  });

  browser.storage.sync.get('displayElo').then((result) => {
    const checked = result.displayElo || false;
    displayEloControl.checked = checked;

    // chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    //   chrome.scripting.executeScript({
    //     target: { tabId: tabs[0].id },
    //     function: () => {
    //       window.displayElo = checked;
    //     },
    //     args: [checked],
    //   });
    // });
  });

  browser.storage.sync.get('displayTimer').then((result) => {
    const checked = result.displayTimer || false;
    displayTimerControl.checked = checked;

    // chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    //   chrome.scripting.executeScript({
    //     target: { tabId: tabs[0].id },
    //     function: () => {
    //       window.displayTimer = checked;
    //     },
    //     args: [checked],
    //   });
    // });
  });

  browser.storage.sync.get('recordGameLog').then((result) => {
    const checked = result.recordGameLog || false;
    recordGameLog.checked = checked;
  });

  disablePlayersControl.addEventListener('change', function () {
    browser.storage.sync.set({ disablePlayers: disablePlayersControl.checked });
  });

  displayEloControl.addEventListener('change', function () {
    browser.storage.sync.set({ displayElo: displayEloControl.checked });
  });

  displayTimerControl.addEventListener('change', function () {
    browser.storage.sync.set({ displayTimer: displayTimerControl.checked });
  });

  recordGameLog.addEventListener('change', function () {
    browser.storage.sync.set({ recordGameLog: recordGameLog.checked });
  });
});
