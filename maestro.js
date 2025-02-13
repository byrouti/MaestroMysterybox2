document.addEventListener("DOMContentLoaded", function () {
    function handleClick() {
        // Get token and prize from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get("token");
        console.log(token)

        const prize = urlParams.get("prize");

        if (!token) {
            alert("No token provided!");
            return;
        }

        // Get used tokens from localStorage
        let usedTokens = JSON.parse(localStorage.getItem("usedTokens")) || [];

        if (usedTokens.includes(token)) {
            // Token already used, show "already-clicked" div and hide "winner"
            document.getElementById("winner").style.display = "none";
            document.getElementById("already-clicked").style.display = "block";
            document.getElementById("already-clicked").textContent = "Oops, frens! You already hit the jackpot once, no double dipping! ";
        } else {
            // Store token in localStorage
            usedTokens.push(token);
            localStorage.setItem("usedTokens", JSON.stringify(usedTokens));

            // Show the prize
            document.getElementById("prize").textContent = prize ? decodeURIComponent(prize) : getRandomPrize();

            // Show "winner" div, hide "already-clicked"
            document.getElementById("winner").style.display = "block";
            document.getElementById("already-clicked").style.display = "none";
        }
    }

    handleClick();  // Run on page load
});

function getRandomPrize() {
    const prizes = [
        "1 Maestro premium account for 1 month",
        "2 Maestro premium account for 1 week",
        "3 Maestro premium account for 1 week",
        "4 Maestro premium account for 1 week",
        "5 Maestro premium account for 1 week",
        "6 Maestro premium account for 1 week",
        "7 Maestro premium account for 3 days",
        "8 Maestro premium account for 3 days",
        "9 Maestro premium account for 1 day",
        "10 Maestro premium account for 1 day"
    ];
    
    return prizes[Math.floor(Math.random() * prizes.length)];
}
