
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
<h1>Extra</h1>
% if extra is not None:
    <p>Extra: {{extra}}</p>
% else:
    <p>No extra data provided.</p>
% end

% for item in items:
    <p>Item: {{item}}</p>
</body>
</html>