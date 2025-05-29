
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<h1>Trading</h1>

<div style="text-align: center;">
            <a href="/" class="btn">Go Home</a>
</div>

<body>
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
</script>

% include("footer.tpl")