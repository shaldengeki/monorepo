var browser = (browser) ? browser : chrome;
const seed = window.location.href.split('table=')[1].split('&')[0];
const replay = window.location.href.includes('/replay');
let arkNova = () => document.title.includes('Ark Nova');

const rand = () => {
  const x = Math.sin(Number(seed)) * 10000;
  return x - Math.floor(x);
};

const randEl = (array, el) => {
  const randomIndex = Math.floor(rand() * (array.length - el.length));
  return array.filter(x => !el.find(ee => ee.includes(x)))[randomIndex];
};

const names1 = ['Enjoyer', 'Enthusiast', 'Believer', 'Expert', 'Specialist'];

const names2 = [
  'Eagle',
  'Rhino',
  'Donkey',
  'Sheep',
  'Tiger',
  'Macaque',
  'Emu',
  'Moose',
  'Sun Bear',
  'Science Lab',
  'Vet',
  'Side Entrance',
  'Native',
  'Release',
  'Breeding Program',
];

let disablePlayers;
browser.storage.sync.get('disablePlayers').then((result) => {
  if (result.disablePlayers) {
    disablePlayers = true;
    observe();
  }
});

let avatars = false;
const playerNames = [];
let logs;
let titlebar;
let gameAction;

const observe = () => {
  if (!replay || !arkNova()) {
    return;
  }

  if (!avatars && disablePlayers) {
    const boards = document.querySelectorAll('.player_board_inner');

    if (boards.length) {
      avatars = true;

      Array.from(document.querySelectorAll('.player_elo_wrap')).forEach(eloWrap => {
        eloWrap.style.display = 'none';
      });

      boards.forEach(board => {
        const pn = board.querySelector('.player-name>a');
        const name = pn.innerText;
        const takenNames = playerNames.map(xs => xs[1]);
        const pseudonym = randEl(names2, takenNames) + ' ' + randEl(names1, takenNames);
        pn.innerHTML = pseudonym;
        playerNames.push([name, pseudonym]);

        const av = board.querySelector('img');
        av.style.display = 'none';
      });
    }
  }

  const logsEl = logs || document.querySelector('#replaylogs');
  logs = logsEl;

  const barEl = titlebar || document.querySelector('#maintitlebar_content');
  titlebar = barEl;

  const gameActionEl = gameAction || document.querySelector('#gameaction_status_wrap');
  gameAction = gameActionEl;

  const replace = span => {
    const txt = span.innerText;
    const match = playerNames.find(xs => xs[0] === txt);
    if (match) span.innerHTML = match[1];
  };

  if (gameActionEl && disablePlayers) {
    Array.from(gameActionEl.querySelectorAll('span')).forEach(replace);
  }

  if (barEl && disablePlayers) {
    Array.from(barEl.querySelectorAll('span')).forEach(replace);
  }

  if (logsEl && disablePlayers) {
    Array.from(logsEl.querySelectorAll('span')).forEach(replace);
  }
};

const observer = new MutationObserver(observe);

if (replay) {
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
}

/// TIMER

const countOccurrences = (string, substring) => {
  return string.split(substring).length - 1;
};

const countOccurrences2 = () => {
  let cnt = 0;
  const loglines = logs.innerText
    .split('\n')
    .reverse()
    .filter(line => {
      return line.length > 16;
    });

  loglines.forEach((line, ix) => {
    if (line.includes('finishing action')) {
      const playerName1 = line.split(' ')[0];
      const next = loglines[ix + 1];
      const playerName2 = next ? next.split(' ')[0] : '';
      if (playerName1 !== playerName2) {
        cnt++;
      }
    }
  });
  return cnt;
};

browser.storage.sync.get('displayTimer').then((result) => {
  displayTimer = result.displayTimer;
});

let displayTimer;
let timer = document.createElement('div');
timer.style.fontSize = '22px';
timer.style.fontFamily = 'MyriadPro-Semibold';
timer.style.fontWeight = 'bold';
timer.style.position = 'absolute';
timer.style.marginTop = '3px';
timer.style.marginLeft = '5px';
timer.style.display = 'none';

const id = setInterval(() => {
  const wrapper = document.querySelector('#break-counter-wrapper');

  if (wrapper) {
    clearInterval(id);
    wrapper.prepend(timer);
  }
}, 500);

setInterval(() => {
  if (logs && displayTimer && !replay && arkNova()) {
    const turns = 1 + Math.floor(countOccurrences2() / 2);
    const rounds = 1 + Math.floor(countOccurrences(logs.innerText, 'End of the break'));
    timer.innerText = `${turns}/${rounds}`;
    timer.style.display = 'block';
  }
}, 500);

/// DISPLAY ELO

let displayElo;
browser.storage.sync.get('displayElo').then((result) => {
  if (result.displayElo) {
    displayElo = true;
  }
});

const id2 = setInterval(() => {
  const boards = Array.from(document.querySelectorAll('.player_board_inner'));

  if (boards.length && displayElo && (replay ? !disablePlayers : true)) {
    boards.forEach(board => {
      const el = board.querySelector('.player_elo_wrap');
      el && (el.style.visibility = 'visible');
    });
  }
}, 500);

/// PLAYER ORDER FIX
fixPlayerOrdering = (intervalId) => {
  const playerBoards = document.getElementsByClassName('ark-player-board-resizable');
  var idOrder = [];
  for (i = 0; i < playerBoards.length; i++) {
    idOrder.push(playerBoards[i].id.replace("player-board-resizable-", ""));
  }

  const playerBoardsContainer = document.getElementById("player_boards");
  const playerBoardConfig = document.getElementById("player_board_config");
  if (playerBoardConfig === null) {
    return;
  }

  const newBoardOrder = [
    playerBoardConfig,
  ].concat(idOrder.map((playerId) => { return document.getElementById("overall_player_board_" + playerId) }));
  newBoardOrder.forEach((elt) => { playerBoardsContainer.appendChild(elt); })

  clearInterval(intervalId);
}
const fixPlayerOrderingInterval = setInterval(() => {
  fixPlayerOrdering(fixPlayerOrderingInterval);
}, 500);

// REPLAY SIDEBAR AT BOTTOM FIX
fixReplaySidebar = (intervalId) => {
  // This happens when the page wrapper gets display:block attached do it,
  // causing the columnar child elements to reserve the entire width of the page instead of living side-by-side.
  const pageWrapper = document.getElementById("#leftright_page_wrapper");
  if (pageWrapper === null) {
    return;
  }

  pageWrapper.style.display = "flex";
  clearInterval(intervalId);
}
const fixReplaySidebarInterval = setInterval(() => {
  fixReplaySidebar(fixReplaySidebarInterval);
}, 500);
