const tabs = document.querySelector(".tabs");
M.Tabs.init(tabs, {});

function prepareForLightTheme(themeToggle) {
    themeToggle.textContent = "🌞 Day Mode";
    themeToggle.href = LIGHT_THEME_URL;
}

function prepareForDarkTheme(themeToggle) {
    themeToggle.textContent = "🌙 Night Mode";
    themeToggle.href = DARK_THEME_URL;
}


function prepareForNextTheme(themeToggle) {

    const pageStyle = window.getComputedStyle(document.body);

    if (pageStyle['backgroundColor'] === "rgb(34, 34, 34)") {
       prepareForLightTheme(themeToggle);
    } else {
      prepareForDarkTheme(themeToggle);
    }
}


document.addEventListener("DOMContentLoaded", function () {

    const searchField = document.querySelector("#search-field");
    const footer = document.querySelector("footer");
    const themeToggle = document.querySelector("#theme-toggle");
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    prepareForNextTheme(themeToggle);

    darkModeMediaQuery.addListener((e) => {

        if(!overide_preferred_color_scheme) {
            const darkModeOn = e.matches;
            darkModeOn ? prepareForLightTheme(themeToggle) : prepareForDarkTheme(themeToggle);
            console.log(`Dark mode is ${darkModeOn ? '🌒 on' : '☀️ off'}.`);
        }
      
    });

    if (screen.width < 600) {

        searchField.addEventListener("focus", function () {
            footer.style.opacity = 0;
        });

        searchField.addEventListener("blur", function () {
            footer.style.opacity = 1;
        })

    }

});


