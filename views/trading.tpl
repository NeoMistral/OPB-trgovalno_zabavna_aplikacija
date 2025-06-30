
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<h1>Portfolio</h1>

<div class="bottom-right">
    <button onclick="openModal('buy')">Buy</button>
    <button onclick="openModal('sell')">Sell</button>
</div>

<!-- Buy Modal -->
<div id="buy" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeModal('buy')">&times;</span>
    <h2>Buy Stock</h2>
    <form id="buy-form">
      <label for="buy-stock">Stock:</label>
      <select id="buy-stock"></select><br><br>

      <label for="buy-amount">Amount:</label>
      <input type="number" id="buy-amount" min="1" required><br><br>

      <p>Total: $<span id="buy-total">0.00</span></p>

      <button type="submit">Confirm Purchase</button>
    </form>
  </div>
</div>

<!-- Sell Modal -->
<div id="sell" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeModal('sell')">&times;</span>
    <h2>Sell Stock</h2>
    <form id="sell-form">
      <label for="sell-stock">Stock:</label>
      <select id="sell-stock"></select><br><br>

      <label for="sell-amount">Amount:</label>
      <input type="number" id="sell-amount" min="1" required><br><br>

      <p>Total: $<span id="sell-total">0.00</span></p>

      <button type="submit">Confirm Sale</button>
    </form>
  </div>
</div>

<div id="user-info" style="margin-bottom: 20px;">
    <!-- JS will populate this -->
</div>

<h2>Portfolio</h2>
<table id="portfolio-table">
    <thead>
        <tr>
            <th>Stock</th>
            <th>Amount Owned</th>
        </tr>
    </thead>
    <tbody>
        <!-- JS will populate this -->
    </tbody>
</table>

<div style="text-align: center;">
    <a href="/" class="btn">Go Home</a>
</div>

<script>

    // Close modal if clicking outside the content
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    }

    async function updateUserPortfolioTable() {
        const response = await fetch('/api/portfolio');
        const data = await response.json();

        if (!Array.isArray(data.portfolio)) {
            console.error("Invalid portfolio format:", data);
            return;
        }

        // Update user info
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `<strong>Logged in as:</strong> ${data.username} <br>
                            <strong>Balance:</strong> $${data.balance.toFixed(2)}`;

        // Update portfolio table
        const tableBody = document.getElementById('portfolio-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';

        data.portfolio.forEach(item => {
            const row = document.createElement('tr');
            const cellSymbol = document.createElement('td');
            const cellAmount = document.createElement('td');

            cellSymbol.textContent = item.symbol;
            cellAmount.textContent = item.amount;

            row.appendChild(cellSymbol);
            row.appendChild(cellAmount);
            tableBody.appendChild(row);
        });
    }
    updateUserPortfolioTable();
    setInterval(updateUserPortfolioTable, 10000); // optional: update every 10s

    let currentPrices = {};

    async function fetchStocks() {
    const res = await fetch('/api/stocks');
    const data = await res.json();
    currentPrices = {};
    const buySelect = document.getElementById('buy-stock');
    const sellSelect = document.getElementById('sell-stock');
    buySelect.innerHTML = '';
    sellSelect.innerHTML = '';

    data.forEach(stock => {
        currentPrices[stock.symbol] = stock.price;

        const optionBuy = document.createElement('option');
        optionBuy.value = stock.symbol;
        optionBuy.textContent = stock.symbol;
        buySelect.appendChild(optionBuy);

        const optionSell = document.createElement('option');
        optionSell.value = stock.symbol;
        optionSell.textContent = stock.symbol;
        sellSelect.appendChild(optionSell);
    });
    }

    function updateTotal(modal) {
    const type = modal === 'buy' ? 'buy' : 'sell';
    const symbol = document.getElementById(`${type}-stock`).value;
    const amount = parseFloat(document.getElementById(`${type}-amount`).value || 0);
    const price = currentPrices[symbol] || 0;
    document.getElementById(`${type}-total`).textContent = (amount * price).toFixed(2);
    }

    document.getElementById('buy-amount').addEventListener('input', () => updateTotal('buy'));
    document.getElementById('buy-stock').addEventListener('change', () => updateTotal('buy'));

    document.getElementById('sell-amount').addEventListener('input', () => updateTotal('sell'));
    document.getElementById('sell-stock').addEventListener('change', () => updateTotal('sell'));

    document.getElementById('buy-form').addEventListener('submit', async function(e) {
        e.preventDefault();

        const symbol = document.getElementById('buy-stock').value;
        const amount = parseInt(document.getElementById('buy-amount').value);
        const price = currentPrices[symbol];

        if (!symbol || isNaN(amount) || amount <= 0) {
            alert('Please enter a valid amount.');
            return;
        }

        const response = await fetch('/api/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, quantity: amount, price })
        });

        const result = await response.json();

        if (response.ok && result.status === 'ok') {
            alert(`Successfully bought ${amount} shares of ${symbol}.`);
            closeModal('buy-modal');
            updateUserPortfolioTable();
        } else {
            alert('Purchase failed: ' + (result.error || 'Unknown error'));
        }
    });

    document.getElementById('sell-form').addEventListener('submit', async function(e) {
        e.preventDefault();

        const symbol = document.getElementById('sell-stock').value;
        const amount = parseInt(document.getElementById('sell-amount').value);
        const price = currentPrices[symbol];

        if (!symbol || isNaN(amount) || amount <= 0) {
            alert('Please enter a valid amount.');
            return;
        }

        const response = await fetch('/api/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, quantity: amount, price })
        });

        const result = await response.json();

        if (response.ok && result.status === 'ok') {
            alert(`Successfully sold ${amount} shares of ${symbol}.`);
            closeModal('sell-modal');
            updateUserPortfolioTable();
        } else {
            alert('Sale failed: ' + (result.error || 'Unknown error'));
        }
    });

    function openModal(id) {
    fetchStocks().then(() => {
        document.getElementById(id).style.display = 'block';
        updateTotal(id);
    });
    }

    function closeModal(id) {
    document.getElementById(id).style.display = 'none';
    }
</script>

% include("footer.tpl")