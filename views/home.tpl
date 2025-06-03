
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<h1>Home</h1>
    <h1>Live Stock Prices</h1>
<table id="stock-table" class="stock-table">
    <thead>
        <tr>
            <th>Stock</th>
            <th>Price</th>
        </tr>
    </thead>
    <tbody>
        <!-- JS will populate this -->
    </tbody>
</table>

<div style="text-align: center;">
    <a href="/poker" class="btnpoker">Go to Poker Page</a>
</div>

<div style="text-align: center;">
    <button id="portfolio-btn" onclick="window.location='/trading'" class="btntrading">Go to portfolio</button>
</div>

<div class="top-right">
    <button onclick="openModal('loginModal')">Login</button>
    <button onclick="openModal('signupModal')">Sign Up</button>
</div>

<!-- Login Modal -->
<div id="loginModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal('loginModal')">&times;</span>
        <h2>Login</h2>
        <form id="login-form" action="/login" method="post">
            <input type="text" name="username" placeholder="Username" required><br><br>
            <input type="password" name="password" placeholder="Password" required><br><br>
            <button type="submit">Log In</button>
        </form>
    </div>
</div>

<!-- Sign Up Modal -->
<div id="signupModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal('signupModal')">&times;</span>
        <h2>Sign Up</h2>
        <form action="/signup" method="post">
            <input type="text" name="username" placeholder="Username" required><br><br>
            <input type="password" name="password" placeholder="Password" required><br><br>
            <button type="submit">Sign Up</button>
        </form>
    </div>
</div>

<script>
    async function updateStockTable() {
        const response = await fetch('/api/stocks');
        const stocks = await response.json();

        const tableBody = document.getElementById('stock-table').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';

        stocks.forEach(stock => {
            const row = document.createElement('tr');
            const cellSymbol = document.createElement('td');
            const cellPrice = document.createElement('td');

            cellSymbol.textContent = stock.symbol;
            cellPrice.textContent = `$${stock.price.toFixed(2)}`;

            row.appendChild(cellSymbol);
            row.appendChild(cellPrice);
            tableBody.appendChild(row);
        });
    }

    updateStockTable();
    setInterval(updateStockTable, 10000); // Refresh every 10s
    function openModal(id) {
        document.getElementById(id).style.display = "block";
    }

    function closeModal(id) {
        document.getElementById(id).style.display = "none";
    }

    // Close modal if clicking outside the content
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    }

    document.getElementById('login-form').addEventListener('submit', async function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const res = await fetch('/login', {
        method: 'POST',
        body: formData
      });

      const result = await res.json();

      if (res.ok && result.status === 'ok') {
        //alert('Login successful!');
        closeModal('loginModal');
        checkLoginStatus();
        // Optionally: refresh portfolio, update UI, etc.
      } else {
        alert('Login failed: ' + (result.error || 'unknown error'));
      }
    });

    async function checkLoginStatus() {
        try {
            const res = await fetch('/api/sessionLogInCheck');
            const data = await res.json();
            if (!data.logged_in) {
                const btn = document.getElementById('portfolio-btn');
                btn.disabled = true;
                btn.textContent = "Login to Access Portfolio";
                btn.classList.add("disabled");
            } else{
                const btn = document.getElementById('portfolio-btn');
                btn.textContent = "Go to portfolio";
                btn.disabled = false;
            }
        } catch (err) {
            console.error('Failed to check login status:', err);
        }
    }

    checkLoginStatus();
</script>
% include("footer.tpl")