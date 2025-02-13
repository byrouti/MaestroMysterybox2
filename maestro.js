document.addEventListener("DOMContentLoaded", function () {
    function handleClick() {
        // Get token and prize from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get("token");
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
            const prizeText = prize ? decodeURIComponent(prize) : getRandomPrize();
            document.getElementById("prize").textContent = prizeText;

            // Show "winner" div, hide "already-clicked"
            document.getElementById("winner").style.display = "block";
            document.getElementById("already-clicked").style.display = "none";
        }
    }

    handleClick();  // Run on page load
});

function getRandomPrize() {
    const prizes = [
        "Maestro premium account for 1 month",
        "Maestro premium account for 1 week",
        "Maestro premium account for 3 days",
        "Maestro premium account for 1 day"
    ];
    return prizes[Math.floor(Math.random() * prizes.length)];
}