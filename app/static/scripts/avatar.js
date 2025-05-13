const avatarContainer = document.querySelector("#avatarContainer");

document.addEventListener("DOMContentLoaded", () => {
    const colors = ["bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-green-500", 
        "bg-teal-500", "bg-blue-500", "bg-indigo-500", "bg-purple-500", "bg-violet-500"
    ];
    
    if (avatarContainer) {
        let nickname = avatarContainer.dataset.nickname;

        const charCodeSum = nickname.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0);
        const avatarColor = colors[charCodeSum % colors.length];

        avatarContainer.classList.add(avatarColor);
        avatarContainer.textContent = nickname[0].toUpperCase();
    }
});
