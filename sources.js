var inspectorElement = null
var titleElement = null
var subscriberElement = null

const touchInfo = { element: null }

window.addEventListener('DOMContentLoaded', () => {
    let parentDocument = window.parent.document

    inspectorElement = parentDocument.getElementById('inspector')
    titleElement = parentDocument.getElementById('inspector-title')
    subscriberElement = parentDocument.getElementById('inspector-subscriber')

    let entries = document.getElementsByClassName('entry')
    for (let entry of entries) {
        entry.addEventListener('mouseenter', hover)
        entry.addEventListener('touchstart', tap)
    }
})

function hover(ev) {
    let tile = ev.currentTarget
    let image = tile.getElementsByTagName('image')[0]
    image.setAttribute('href', image.dataset.href)
    let title = tile.dataset.title
    let subscriber = tile.dataset.subscriber
    unhover(undefined)
    titleElement.innerText = title
    subscriberElement.innerText = subscriber
    inspectorElement.classList.remove('hidden')
}

function tap(ev) {
    let tile = ev.currentTarget
    if (touchInfo.element !== tile) {
        ev.preventDefault()
        touchInfo.element = tile
    }
    hover(ev)
}

function unhover(ev) {
    inspectorElement.classList.add('hidden')
}
