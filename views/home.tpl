<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <!-- Link to CSS stylesheet -->
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Home</h1>

    <!-- Stock prices live table -->
    <h1>Live Stock Prices</h1>
    <table id="stock-table" class="stock-table">
        <thead>
            <tr>
                <!-- 3 columns of Stock + Price -->
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

    <!-- Buttons for navigation -->
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
        <button id="poker-btn" onclick="window.location='/poker'" class="btnpoker">Go to Poker Page</button>
        <button id="portfolio-btn" onclick="window.location='/trading'" class="btntrading">Go to Portfolio</button>
    </div>

    <!-- Login / Sign-up buttons in top-right -->
    <div class="top-right">
        <button onclick="openModal('loginModal')">Login</button>
        <button onclick="openModal('signupModal')">Sign Up</button>
    </div>

    <!-- ================= LOGIN MODAL ================= -->
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

    <!-- ================= SIGNUP MODAL ================= -->
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
        /**
         * Fetch stock prices from API and render them in the table.
         * Displays 3 stocks per row with their prices.
         */
        async function updateStockTable() {
            const response = await fetch('/api/stocks');
            const stocks = await response.json();

            const tableBody = document.getElementById('stock-table').getElementsByTagName('tbody')[0];
            tableBody.innerHTML = '';

            // Render rows of 3 stocks (6 cells per row: Stock, Price * 3)
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
                        // Fill empty cells if remaining stocks < 3
                        row.appendChild(document.createElement('td'));
                        row.appendChild(document.createElement('td'));
                    }
                }

                tableBody.appendChild(row);
            }
        }

        // Load stock prices on page load and refresh every 10s
        updateStockTable();
        setInterval(updateStockTable, 10000);

        // Open modal by ID
        function openModal(id) {
            document.getElementById(id).style.display = "block";
        }

        // Close modal by ID
        function closeModal(id) {
            document.getElementById(id).style.display = "none";
        }

        // Close modal if user clicks outside modal content
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = "none";
            }
        }

        /**
         * LOGIN FORM
         * Submits username/password via fetch to /login,
         * handles success/failure, and updates UI accordingly.
         */
        document.getElementById('login-form').addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const res = await fetch('/login', {
                method: 'POST',
                body: formData
            });

            const result = await res.json();

            if (res.ok && result.status === 'ok') {
                closeModal('loginModal');
                checkLoginStatus(); // Update button states after login
            } else {
                alert('Login failed: ' + (result.error || 'unknown error'));
            }
        });

        /**
         * SIGNUP FORM
         * Sends username/password to /signup,
         * if successful closes modal, otherwise shows error.
         */
        document.getElementById('signup-form').addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const res = await fetch('/signup', {
                method: 'POST',
                body: formData
            });

            const result = await res.json();

            if (res.ok && result.error === "ok") {
                closeModal('signupModal');
            } else {
                alert('Sign-up failed: ' + (result.error || 'unknown error'));
            }
        });

        /**
         * Check if user is logged in.
         * If not logged in: disable Poker + Portfolio buttons.
         * If logged in: enable them.
         */
        async function checkLoginStatus() {
            try {
                const res = await fetch('/api/sessionLogInCheck');
                const data = await res.json();

                if (!data.logged_in) {
                    const btn = document.getElementById('portfolio-btn');
                    const btn2 = document.getElementById('poker-btn');
                    btn.disabled = true;
                    btn.textContent = "Login to Access Portfolio";
                    btn.classList.add("disabled");

                    btn2.disabled = true;
                    btn2.textContent = "Login to Access Poker";
                    btn2.classList.add("disabled");
                } else {
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

        // Run login check on page load
        checkLoginStatus();
    </script>

    <!-- Footer template included -->
    % include("footer.tpl")
</body>
</html>
