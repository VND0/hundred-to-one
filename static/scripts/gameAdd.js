let questionsCounter = 0;

const listTitle = document.querySelector("#listTitle")
const questionsList = document.querySelectorAll("#questionsList>li")
const addButton = document.querySelector("#addButton")

function changesCounterUpdate() {
    listTitle.innerText = `Вопросы для игры (${questionsCounter} / 7)`

    if (questionsCounter === 7) {
        listTitle.classList.add("divider-secondary")
        listTitle.classList.remove("divider-error")

        addButton.classList.remove("btn-disabled")
    } else {
        listTitle.classList.add("divider-error")
        listTitle.classList.remove("divider-secondary")

        addButton.classList.add("btn-disabled")
    }
}

function countCheckbox(input, doDecrement = true) {
    if (input.checked) {
        questionsCounter++
    } else if (doDecrement) {
        questionsCounter--
    }
}

questionsList.forEach((elem) => {
    const input = elem.querySelector("input")
    countCheckbox(input, false)

    input.addEventListener("change", () => {
        countCheckbox(input)
        changesCounterUpdate()
    })
})

changesCounterUpdate()
