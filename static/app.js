var subwayLinesTable = document.getElementById("subway-lines"),
    stationButtons = subwayLinesTable.getElementsByTagName("td"),
    activeStationButton = null,
    sourceInput = document.getElementById("source"),
    locationInput = document.getElementById("location"),
    submitButton = document.getElementById("submit"),
    responseFrame = document.getElementById("response-frame"),
    station = "northeastern";

// selector constructor
function buildSelector(containingTable, options, callback, label_index_adjust = 1) {
    var newRow = document.createElement("tr");
    for (var i = 0; i < options.length; i++) {
        var thisOption = options[i];
        td = document.createElement("td");
        td.innerHTML = thisOption + " (" + (i + label_index_adjust) +  ")";
        (function(option) {
            td.onclick = function() {
                callback(option);
            }
        })(thisOption);
        newRow.appendChild(td);
    }
    containingTable.appendChild(newRow);
}

// construct status selector
var statusSelector = document.getElementById("status-selector"),
    statusInput = document.getElementById("status"),
    locations = ["entering", "stopped", "leaving", "left"],
    location_ = "stopped";
buildSelector(statusSelector, locations, function(option) {
    location_ = option;
    update();
});
var statusButtons = statusSelector.getElementsByTagName("td");

// construct position selector
var positionSelector = document.getElementById("position-selector"),
    positionInput = document.getElementById("position"),
    positions = ["subway car", "platform center", "platform entrance", "platform exit"],
    position = "subway car";
buildSelector(positionSelector, positions, function(option) {
    position = option;
    update();
}, 5);
var positionButtons = positionSelector.getElementsByTagName("td");

function updateSelector(selectorButtons, selectedButtonText) {
    for (var j = 0; j < selectorButtons.length; j++) {
        var selectorButton = selectorButtons[j];
        if (selectorButton.innerHTML.startsWith(selectedButtonText)) {
            selectorButton.setAttribute("class", "selected-status");
        } else {
            selectorButton.removeAttribute("class");
        }
    }
}

// update the forms and ui to reflect inputs
function update() {
    locationInput.value = station;
    statusInput.value = location_;
    positionInput.value = position;

    for (var i = 0; i < stationButtons.length; i++) {
        var stationButton = stationButtons[i];
        if (stationButton.innerHTML == station) {
            activeStationButton = stationButton;
            stationButton.setAttribute("class", "selector-active");
        } else if (stationButton.innerHTML.length != 0) {
            stationButton.removeAttribute("class");
        }
    }

    updateSelector(statusButtons, location_);
    updateSelector(positionButtons, position);
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
                update();
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
            if (i <= locations.length) {
                location_ = locations[i - 1];
                update();
            } else if (i <= positions.length + 4) {
                position = positions[i - 5];
                update();
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
                        update();
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

update();
