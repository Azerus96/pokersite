/* Стиль фона и основного контейнера */
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    color: #333;
    margin: 0;
    padding: 20px;
    text-align: center;
}

h1, h2, label {
    color: #444;
}

/* Стили для формы регистрации */
form {
    display: inline-block;
    margin-top: 20px;
}

input[type="text"] {
    padding: 10px;
    width: 250px;
    margin: 5px;
    border-radius: 5px;
    border: 1px solid #ddd;
}

input[type="submit"] {
    padding: 10px 20px;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

input[type="submit"]:hover {
    background-color: #0056b3;
}

/* Стол и позиции игроков */
#poker-table {
    position: relative;
    width: 600px;
    height: 600px;
    background-color: green;
    border-radius: 50%;
    margin: 30px auto;
    border: 5px solid #003300;
}

.player-slot {
    position: absolute;
    width: 120px;
    height: 80px;
    background-color: lightgrey;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}

#player-1 { top: 10%; left: 50%; transform: translate(-50%, -50%); }
#player-2 { top: 30%; right: 10%; }
#player-3 { top: 50%; right: 10%; }
#player-4 { bottom: 30%; right: 10%; }
#player-5 { bottom: 10%; left: 50%; transform: translate(-50%, -50%); }
#player-6 { bottom: 30%; left: 10%; }
#player-7 { top: 50%; left: 10%; }
#player-8 { top: 30%; left: 10%; }

/* Стили для карт */
.player-cards img {
    width: 30px;
    height: 40px;
    margin-left: 5px;
}

/* Стили для интерактивных кнопок фолда, колла, рейза */
#player-actions {
    display: flex;
    justify-content: center;
    margin-top: 30px;
}

button {
    padding: 10px 20px;
    margin: 0 20px;
    font-size: 16px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #218838;
}

#raise-wrapper {
    display: inline-block;
    text-align: center;
}

input[type="range"] {
    -webkit-appearance: none;
    width: 200px;
    height: 8px;
    background: #ddd;
    outline: none;
    border-radius: 5px;
    transition: background 0.3s;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: #007BFF;
    border-radius: 50%;
    cursor: pointer;
}

input[type="range"]:hover {
    background: #ccc;
}
