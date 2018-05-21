var subwayLinesTable = document.getElementById("subway-lines"),
    stationButtons = subwayLinesTable.getElementsByTagName("td"),
    activeStationButton = null,
    sourceInput = document.getElementById("source"),
    statusInput = document.getElementById("status"),
    locationInput = document.getElementById("location"),
    positionInput = document.getElementById("position"),
    submitButton = document.getElementById("submit"),
    responseFrame = document.getElementById("response-frame"),
    station = "northeastern";

function Selector(containingTable, options, defaultOption = 1, label_index_adjust = 1) {
    this.options = options;
    this.activeOption = this.options[defaultOption];
    this.buttons = [];

    var newRow = document.createElement("tr"),
        selector = this,
        firstUpdate = true;

    this.selectOption = function(option) {
        this.activeOption = option;
        for (var j = 0; j < this.buttons.length; j++) {
            var button = this.buttons[j];
            if (button.innerHTML.startsWith(option)) {
                button.setAttribute("class", "selected-status");
            } else {
                button.removeAttribute("class");
            }
        }
        if (firstUpdate) {
            firstUpdate = false;
        } else {
            updateForms();
        }
    }

    for (var i = 0; i < options.length; i++) {
        var thisOption = options[i];
        td = document.createElement("td");
        td.innerHTML = thisOption + " (" + (i + label_index_adjust) +  ")";
        (function(selector, option) {
            td.onclick = function() {
                selector.selectOption(option);
            }
        })(selector, thisOption);
        newRow.appendChild(td);
        this.buttons.push(td);
    }

    containingTable.appendChild(newRow);
    this.selectOption(this.activeOption);
}

var statusSelector = new Selector(
    document.getElementById("status-selector"),
    ["entering", "stopped", "leaving", "left"],
    1
);
var positionSelector = new Selector(
    document.getElementById("position-selector"),
    ["subway car", "platform center", "platform entrance", "platform exit"],
    0, 5
);

// update the forms and ui to reflect inputs
function updateForms() {
    locationInput.value = station;
    statusInput.value = statusSelector.activeOption;
    positionInput.value = positionSelector.activeOption;

    for (var i = 0; i < stationButtons.length; i++) {
        var stationButton = stationButtons[i];
        if (stationButton.innerHTML == station) {
            activeStationButton = stationButton;
            stationButton.setAttribute("class", "selector-active");
        } else if (stationButton.innerHTML.length != 0) {
            stationButton.removeAttribute("class");
        }
    }
}

// station selector
for (var i = 0; i < stationButtons.length; i++) {
    var stationButton = stationButtons[i];
    var thisStation = stationButton.innerHTML;

    // make blank stationButtons invisible
    if (thisStation.length == 0) {
        stationButton.setAttribute("class", "blank");

    // connect events to other stationButtons
    } else {
        (function(thisStation) {
            stationButton.onclick = function() {
                station = thisStation;
                updateForms();
            }
        })(thisStation);
    }

}

var stationButtonsTable = [];
var lines = subwayLinesTable.getElementsByTagName("tr");
for (var i = 0; i < lines.length; i++) {
    stationButtonsTable.push(lines[i].getElementsByTagName("td"));
}

function findTableCoordinates() {
    for (var i = 0; i < stationButtonsTable.length; i++) {
        var line = stationButtonsTable[i]
        for (var j = 0; j < line.length; j++) {
            if (line[j] == activeStationButton) {
                return [i, j];
            }
        }
    }
}

function stationTableNav(xDirection, yDirection) {
    var coords = findTableCoordinates();
    console.log(coords);
    var newButton = stationButtonsTable[coords[0] + yDirection][coords[1] + xDirection];
    console.log(coords[0] + yDirection);
    if (newButton !== undefined) {
        newButton.click();
        newButton.scrollIntoView();
    }
}

// keybindings
document.onkeydown = function(e) {
    // ignore input for fields
    if (e.target == document.body) {
        console.log(e.key, e.target);
        var i = parseInt(e.key);
        if (Number.isInteger(i)) {
            if (i <= statusSelector.options.length) {
                statusSelector.selectOption(statusSelector.options[i - 1]);
            } else if (i <= positionSelector.options.length + 4) {
                positionSelector.selectOption(positionSelector.options[i - 1 - statusSelector.options.length]);
            }
        } else switch(e.key) {
            case "Enter":
                submitButton.click();
                break;
            case "Tab":
                e.preventDefault();
                for (var i = 0; i < statusButtons.length; i++) {
                    if (locations[i] == location_) {
                        location_ = locations[(i + 1) % locations.length];
                        updateForms();
                        break;
                    }
                }
                break;
            case "h":
            case "ArrowLeft":
                stationTableNav(-1, 0);
                break;
            case "j":
            case "ArrowDown":
                stationTableNav(0, 1);
                break;
            case "k":
            case "ArrowUp":
                stationTableNav(0, -1);
                break;
            case "l":
            case "ArrowRight":
                stationTableNav(1, 0);
                break;
            default:
                break;
        }
    }
}

updateForms();
