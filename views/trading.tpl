<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <!-- Global stylesheet -->
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<h1>Portfolio</h1>

<!-- Buttons to open Buy/Sell modals -->
<div class="bottom-right">
    <button onclick="openModal('buy')">Buy</button>
    <button onclick="openModal('sell')">Sell</button>
</div>

<!-- ================= BUY MODAL ================= -->
<div id="buy" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeModal('buy')">&times;</span>
    <h2>Buy Stock</h2>
    <form id="buy-form">
      <!-- Dropdown populated with stock list -->
      <label for="buy-stock">Stock:</label>
      <select id="buy-stock"></select><br><br>

      <!-- Quantity input -->
      <label for="buy-amount">Amount:</label>
      <input type="number" id="buy-amount" min="1" required><br><br>

      <!-- Real-time calculated total -->
      <p>Total: $<span id="buy-total">0.00</span></p>

      <button type="submit">Confirm Purchase</button>
    </form>
  </div>
</div>

<!-- ================= SELL MODAL ================= -->
<div id="sell" class="modal">
  <div class="modal-content">
    <span class="close" onclick="closeModal('sell')">&times;</span>
    <h2>Sell Stock</h2>
    <form id="sell-form">
      <!-- Dropdown populated with stock list -->
      <label for="sell-stock">Stock:</label>
      <select id="sell-stock"></select><br><br>

      <!-- Quantity input -->
      <label for="sell-amount">Amount:</label>
      <input type="number" id="sell-amount" min="1" required><br><br>

      <!-- Real-time calculated total -->
      <p>Total: $<span id="sell-total">0.00</span></p>

      <button type="submit">Confirm Sale</button>
    </form>
  </div>
</div>

<!-- Logged-in user info (username + balance) -->
<div id="user-info" style="margin-bottom: 20px;">
    <!-- JS will populate this -->
</div>

<!-- Portfolio Table (3-column layout repeated horizontally) -->
<table id="portfolio-table">
    <thead>
        <tr>
            <th>Symbol</th>
            <th>Amount</th>
            <th>Value</th>
            <th>Symbol</th>
            <th>Amount</th>
            <th>Value</th>
            <th>Symbol</th>
            <th>Amount</th>
            <th>Value</th>
        </tr>
    </thead>
    <tbody>
        <!-- JS will populate rows -->
    </tbody>
</table>

<!-- Navigation back to home -->
<div style="text-align: center;">
    <a href="/" class="btn">Go Home</a>
</div>

<script>
    // Close modal if clicking outside modal content
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    }

    /**
     * Utility: format number as money
     */
    function formatMoney(value, fallback = '0.00') {
        const num = typeof value === 'number' ? value : Number(value);
        return Number.isFinite(num) ? num.toFixed(2) : fallback;
    }

    /**
     * Fetch user portfolio and update UI table + user info.
     */
    async function updateUserPortfolioTable() {
        const response = await fetch('/api/portfolio');
        const data = await response.json();

        if (!Array.isArray(data.portfolio)) {
            console.error("Invalid portfolio format:", data);
            return;
        }
        console.log("API data:", data);

        // Update logged-in user info (username + balance)
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `<strong>Logged in as:</strong> ${data.username} <br>
                            <strong>Balance:</strong> $${formatMoney(data.balance)}`;

        // Update portfolio table
        const tableBody = document.getElementById('portfolio-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';

        // Display stocks 3 per row
        for (let i = 0; i < data.portfolio.length; i += 3) {
            const row = document.createElement('tr')

            for (let j=0; j<3; j++) {
                if (i+j < data.portfolio.length){
                    const cellSymbol = document.createElement('td');
                    const cellAmount = document.createElement('td');
                    const cellPrice = document.createElement('td');
                    cellSymbol.textContent = data.portfolio[i+j].symbol;
                    cellAmount.textContent = data.portfolio[i+j].amount;
                    cellPrice.textContent = `$${data.portfolio[i+j].value}`;

                    row.appendChild(cellSymbol);
                    row.appendChild(cellAmount);
                    row.appendChild(cellPrice)
                    tableBody.appendChild(row);
                } else {
                    // Fill empty cells if portfolio length not multiple of 3
                    row.appendChild(document.createElement('td'));
                    row.appendChild(document.createElement('td'));
                    row.appendChild(document.createElement('td'));
                }
            }
        }
    }

    // Initial load + refresh every 10 seconds
    updateUserPortfolioTable();
    setInterval(updateUserPortfolioTable, 10000);

    /**
     * Keep stock prices cached locally (used for buy/sell totals).
     */
    let currentPrices = {};

    /**
     * Fetch all available stocks (from backend) and populate dropdowns.
     */
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

            // Populate buy select
            const optionBuy = document.createElement('option');
            optionBuy.value = stock.symbol;
            optionBuy.textContent = stock.symbol;
            buySelect.appendChild(optionBuy);

            // Populate sell select
            const optionSell = document.createElement('option');
            optionSell.value = stock.symbol;
            optionSell.textContent = stock.symbol;
            sellSelect.appendChild(optionSell);
        });
    }

    /**
     * Update "total" price shown inside buy/sell modals.
     */
    function updateTotal(modal) {
        const type = modal === 'buy' ? 'buy' : 'sell';
        const symbol = document.getElementById(`${type}-stock`).value;
        const amount = parseFloat(document.getElementById(`${type}-amount`).value || 0);
        const price = currentPrices[symbol] || 0;
        document.getElementById(`${type}-total`).textContent = (amount * price).toFixed(2);
    }

    // Live update totals when stock/amount changes
    document.getElementById('buy-amount').addEventListener('input', () => updateTotal('buy'));
    document.getElementById('buy-stock').addEventListener('change', () => updateTotal('buy'));

    document.getElementById('sell-amount').addEventListener('input', () => updateTotal('sell'));
    document.getElementById('sell-stock').addEventListener('change', () => updateTotal('sell'));

    /**
     * Handle Buy form submission
     */
    document.getElementById('buy-form').addEventListener('submit', async function(e) {
        e.preventDefault();

        const symbol = document.getElementById('buy-stock').value;
        const amount = parseInt(document.getElementById('buy-amount').value);
        const price = currentPrices[symbol];

        // Basic validation
        if (!symbol || isNaN(amount) || amount <= 0) {
            alert('Please enter a valid amount.');
            return;
        }

        // Send to backend
        const response = await fetch('/api/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, quantity: amount, price })
        });

        const result = await response.json();

        if (response.ok && result.status === 'ok') {
            alert(`Successfully bought ${amount} shares of ${symbol}.`);
            closeModal('buy'); // close after success
            updateUserPortfolioTable();
        } else {
            alert('Purchase failed: ' + (result.error || 'Unknown error'));
        }
    });

    /**
     * Handle Sell form submission
     */
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
            closeModal('sell'); // close after success
            updateUserPortfolioTable();
        } else {
            alert('Sale failed: ' + (result.error || 'Unknown error'));
        }
    });

    /**
     * Open modal → fetch stock list first, then show modal
     */
    function openModal(id) {
        fetchStocks().then(() => {
            document.getElementById(id).style.display = 'block';
            updateTotal(id);
        });
    }

    /**
     * Close modal
     */
    function closeModal(id) {
        document.getElementById(id).style.display = 'none';
    }
</script>

<!-- Shared footer -->
% include("footer.tpl")
</body>
</html>
