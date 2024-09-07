document.addEventListener('DOMContentLoaded', function () {
  const disablePlayersControl = document.getElementById('hidePlayers');
  const displayEloControl = document.getElementById('displayElo');
  const displayTimerControl = document.getElementById('displayTimer');

  chrome.storage.sync.get(['disablePlayers'], function (result) {
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

  chrome.storage.sync.get(['displayElo'], function (result) {
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

  chrome.storage.sync.get(['displayTimer'], function (result) {
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

  disablePlayersControl.addEventListener('change', function () {
    chrome.storage.sync.set({ disablePlayers: disablePlayersControl.checked });
  });

  displayEloControl.addEventListener('change', function () {
    chrome.storage.sync.set({ displayElo: displayEloControl.checked });
  });

  displayTimerControl.addEventListener('change', function () {
    chrome.storage.sync.set({ displayTimer: displayTimerControl.checked });
  });
});
