<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1> Texas Hold'em Poker</h1>
<div class="table-container">

    
    <!-- Card Layout -->
    <div class="card-area">
        
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
        <div class="button-box">
            <button class ="btn" onclick="dealCards()">Deal Cards</button>
            <button class ="btn" onclick="showCards()">Check</button>
            <button class ="btn">Raise</button>
        </div>

        <div style="text-align: center;">
            <a href="/" class="btn">Go Home</a>
        </div>
    </div>
    
</div>

<script>
function showCards() {
    fetch('/api/check')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
        });
}

function dealCards() {
    fetch('/api/deal')
        .then(response => response.json())
        .then(data => {
            updateCards('top-cards', data.dealer);
            updateCards('middle-cards', data.community);
            updateCards('bottom-cards', data.player);
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
</script>

% include("footer.tpl")