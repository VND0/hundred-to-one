const themeController = document.querySelector(".theme-controller");


document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);

    if (savedTheme === "light") {
        themeController.checked = true;
    }
    else {
        themeController.checked = false;
    }
});


themeController.addEventListener("click", () => {
    let currentTheme = localStorage.getItem("theme");
    let newTheme = currentTheme === "light" ? "dark" : "light";

    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
});
