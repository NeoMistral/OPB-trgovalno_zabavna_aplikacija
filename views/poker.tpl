<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="table-container">

    <!-- Card Layout -->
    <div class="card-area">
        <h1> Texas Hold'em Poker</h1>
        <div class="card-section">
            <h2>Dealer</h2>
            <div class="top-cards" id="top-cards">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
            </div>
        </div>
    
        <div class="card-section">
            <h2>Community</h2>
            <div class="middle-cards" id="middle-cards">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
            </div>
        </div>
    
        <div class="card-section">
            <h2>Player</h2>
            <div class="bottom-cards" id="bottom-cards">
                <img src="/static/cards/Hidden.png" class="card">
                <img src="/static/cards/Hidden.png" class="card">
            </div>
        </div>
    </div>

    <!-- Sidebar with Buttons -->
    <div class="sidebar">
        <!-- Game Info -->
        <div class="game-info">
            <p id="game-ante">Ante: None</p>
            <p id="game-blind">Blind: None</p>
            <p id="game-bet">Bet: None</p>
            <p id="game-winner">Winner: TBD</p>
            <p id="game-winnings">Winnings: None</p>
            <label>
                Stock:
                <select id="stock-input"></select>
            </label><br>
            <p id="game-budget">Num of stocks: 0</p>
            <!-- Input fields for blind and ante -->
            <label>
                Blind:
                <input type="number" id="blind-input" min="1" value="1">
            </label><br>

            <label>
                Ante:
                <input type="number" id="ante-input" min="1" value="1">
            </label><br>

            <button id="btn-set_values" class="btn" onclick="setGameSettings()">Set Values</button>
        </div>

        <div class="button-box">
            <button id="btn-deal_cards" class ="btn" onclick="dealCards()" disabled>Deal Cards</button>
            <button id="btn-check" class ="btn" onclick="check()" disabled>Check</button>
            <button id="btn-bet" class ="btn" onclick="bet()" disabled>Bet</button>
        </div>

        <div style="text-align: center;">
            <a href="/" class="btn">Go Home</a>
        </div>
    </div>
    
</div>

<script>
function bet() {
    fetch('/api/bet')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
            updateGameInfo();
        });
}

function check() {
    fetch('/api/check')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
            updateGameInfo();
        });
}

function dealCards() {
    fetch('/api/deal')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
            updateGameInfo();
        });
}

function setGameSettings() {
    const blind = parseInt(document.getElementById('blind-input').value);
    const ante = parseInt(document.getElementById('ante-input').value);
    const budget = document.getElementById('game-budget').value;
    const stock = document.getElementById('stock-input').value;

    fetch('/api/set_game_settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blind, ante, stock, budget})
    })
    .then(res => res.json())
    .then(data => {
        check_if_can_bet();
        updateGameInfo(); // Refresh game info
    })
    .catch(err => console.error("Failed to set settings", err));
}

function updateGameInfo() {
    fetch('/api/game-state') // Adjust path as needed
        .then(res => res.json())
        .then(data => {
            document.getElementById('game-bet').textContent = `Bet: ${data.bet}`;
            document.getElementById('game-budget').textContent = `Num of stocks: ${data.budget}`;
            document.getElementById('game-ante').textContent = `Blind: ${data.blind}`;
            document.getElementById('game-blind').textContent = `Ante: ${data.ante}`;
            document.getElementById('game-winner').textContent = `Winner: ${data.winner || 'TBD'}`;
            document.getElementById('game-winnings').textContent = `Winnings: ${data.won}`;

            const dealBtn = document.getElementById("btn-deal_cards");
            const checkBtn = document.getElementById("btn-check");
            const betBtn = document.getElementById("btn-bet");
            const setValuesBtn = document.getElementById("btn-set_values")
            
            if (data.round === 0){
                dealBtn.disabled = true, checkBtn.disabled = false;
                betBtn.disabled = false, setValuesBtn.disabled = true;
                checkBtn.innerText = "Check";
                checkBtn.setAttribute("onclick", "check()");
            } else if (data.round === 1){
                checkBtn.disabled = false, betBtn.disabled = false;
            } else if (data.round === 2){
                checkBtn.disabled = false, betBtn.disabled = false;
                checkBtn.innerText = "Fold";
                checkBtn.setAttribute("onclick", "fold()");
            } else if (data.round === -1) {
                betBtn.disabled = true, checkBtn.disabled = true;
                dealBtn.disabled = false;
                setValuesBtn.disabled = false;
                checkBtn.innerText = "Check";
                checkBtn.setAttribute("onclick", "check()");
            } else if (data.round === -2) {
                betBtn.disabled = true, checkBtn.disabled = true;
                dealBtn.disabled = true;
                setValuesBtn.disabled = false;
                checkBtn.innerText = "Check";
                checkBtn.setAttribute("onclick", "check()");
            } else {
                dealBtn.disabled = false, checkBtn.disabled = true;
                betBtn.disabled = true, setValuesBtn.disabled = false;
            }
        })
        .catch(err => console.error("Failed to load game state", err));
}

function check_if_can_bet() {
  fetch('/api/canBuy', { method: 'POST' }) // or GET if you kept it allowed
    .then(res => res.json())
    .then(data => {
      const canBet = data.can === true;

      const dealBtn = document.getElementById("btn-deal_cards");
      const checkBtn = document.getElementById("btn-check");
      const betBtn = document.getElementById("btn-bet");
      const setValuesBtn = document.getElementById("btn-set_values");

      if (canBet) {
        dealBtn.disabled = true;
        checkBtn.disabled = false;
        betBtn.disabled = false;
        setValuesBtn.disabled = true;
      } else {
        dealBtn.disabled = true;
        checkBtn.disabled = true;
        betBtn.disabled = true;
        setValuesBtn.disabled = false;
        alert('Insufficient funds');
      }
    })
    .catch(err => console.error("Failed to check bet state", err));
}

function fold() {
    fetch('/api/fold')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
            updateGameInfo();
        });
}

function updateCards(containerId, cards) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';  // Clear old cards
    cards.forEach(card => {
        const img = document.createElement('img');
        img.src = `/static/cards/${card}.png`;
        img.alt = card;
        img.className = 'card';
        container.appendChild(img);
    });
}

async function getStockOptions() {
    // This would be done asynchronously, e.g., with fetch
    const response = await fetch('/api/portfolio');
    const userData = await response.json();
    return userData
}

// Call backend to get updated budget
async function updateBudget(stock) {
    const res = await fetch('/api/budget', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ stock: stock })
    });

    const data = await res.json();
    document.getElementById('game-budget').textContent = `Num od stocks: ${data.budget}`;
}

async function populateStockOptions() {
    const stockSelect = document.getElementById('stock-input');
    stockSelect.innerHTML = ''; // Clear existing options

    const userData = await getStockOptions(); // Await the async call
    const portfolio = userData.portfolio
    portfolio.forEach(stock => {
        const option = document.createElement('option');
        option.value = stock.symbol; // or stock.id, depending on your data
        option.textContent = stock.symbol; // Display symbol in the dropdown
        stockSelect.appendChild(option);
    });

}

    // Setup event listeners
    document.addEventListener('DOMContentLoaded', () => {
        populateStockOptions();

        document.getElementById('stock-input').addEventListener('change', function () {
            updateBudget(this.value);
        });
    });

</script>

% include("footer.tpl")