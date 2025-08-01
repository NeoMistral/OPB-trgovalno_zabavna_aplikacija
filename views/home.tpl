
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
            <th>Stock</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Price</th>
        </tr>
    </thead>
    <tbody>
        <!-- JS will populate this -->
    </tbody>
</table>

<div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
    <button id="poker-btn" onclick="window.location='/poker'" class="btnpoker">Go to Poker Page</button>
    <button id="portfolio-btn" onclick="window.location='/trading'" class="btntrading">Go to Portfolio</button>
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
        <form id="signup-form" action="/signup" method="post">
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

        for (let i = 0; i < stocks.length; i += 3) {
            const row = document.createElement('tr');

            for (let j = 0; j < 3; j++) {
                if (i + j < stocks.length) {
                    const cellSymbol = document.createElement('td');
                    const cellPrice = document.createElement('td');

                    cellSymbol.textContent = stocks[i + j].symbol;
                    cellPrice.textContent = `$${stocks[i + j].price.toFixed(2)}`;

                    row.appendChild(cellSymbol);
                    row.appendChild(cellPrice);
                } else {
                    // Fill empty cells if remaining stocks are less than 3
                    row.appendChild(document.createElement('td'));
                    row.appendChild(document.createElement('td'));
                }
            }

            tableBody.appendChild(row);
        }
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

    document.getElementById('signup-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const res = await fetch('/signup', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();

        if (res.ok && result.status === 'ok') {
            //alert('Sign-up successful! You can now log in.');
            closeModal('signupModal');
        } else {
            alert('Sign-up failed: ' + (result.error || 'unknown error'));
        }
    });

    async function checkLoginStatus() {
        try {
            const res = await fetch('/api/sessionLogInCheck');
            const data = await res.json();
            if (!data.logged_in) {
                const btn = document.getElementById('portfolio-btn');
                const btn2 = document.getElementById('poker-btn')
                btn.disabled = true;
                btn.textContent = "Login to Access Portfolio";
                btn.classList.add("disabled");
                btn2.disabled = true;
                btn2.textContent = "Login to Access Poker";
                btn2.classList.add("disabled");
            } else{
                const btn = document.getElementById('portfolio-btn');
                btn.textContent = "Go to portfolio";
                btn.disabled = false;
                const btn2 = document.getElementById('poker-btn');
                btn2.textContent = "Go to Poker";
                btn2.disabled = false;
            }
        } catch (err) {
            console.error('Failed to check login status:', err);
        }
    }

    checkLoginStatus();
</script>
% include("footer.tpl")