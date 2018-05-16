var subwayLinesTable = document.getElementById("subway-lines"),
    stationButtons = subwayLinesTable.getElementsByTagName("td"),
    activeStationButton = null,
    sourceInput = document.getElementById("source"),
    locationInput = document.getElementById("location"),
    submitButton = document.getElementById("submit"),
    responseFrame = document.getElementById("response-frame"),
    stationName = "northeastern";

var statusSelector = document.getElementById("status-selector"),
    statusInput = document.getElementById("status"),
    locationStatuses = ["stopped", "entering", "leaving", "left"],
    locationStatus = "stopped";

// update the forms and ui to reflect inputs
function updateLocation() {
    locationInput.value = stationName;
    statusInput.value = locationStatus;

    statusButtons = statusSelector.getElementsByTagName("td");
    for (var j = 0; j < statusButtons.length; j++) {
        var statusButton = statusButtons[j];
        if (statusButton.innerHTML.startsWith(locationStatus)) {
            statusButton.setAttribute("class", "selected-status");
        } else {
            statusButton.removeAttribute("class");
        }
    }

    for (var i = 0; i < stationButtons.length; i++) {
        var stationButton = stationButtons[i];
        if (stationButton.innerHTML == stationName) {
            activeStationButton = stationButton;
            stationButton.setAttribute("class", "selected-station");
        } else if (stationButton.innerHTML.length != 0) {
            stationButton.removeAttribute("class");
        }
    }
}

// status selector
var newRow = document.createElement("tr");
statusSelector.appendChild(newRow);

for (var i = 0; i < locationStatuses.length; i++) {
    var thisLocationStatus = locationStatuses[i];
    td = document.createElement("td");
    td.innerHTML = thisLocationStatus + " (" + i +  ")";
    (function(thisLocationStatus) {
        td.onclick = function() {
            locationStatus = thisLocationStatus;
            updateLocation();
        }
    })(thisLocationStatus);
    statusSelector.appendChild(td);
}

// station selector
for (var i = 0; i < stationButtons.length; i++) {
    var stationButton = stationButtons[i];
    var thisStationName = stationButton.innerHTML;

    // make blank stationButtons invisible
    if (thisStationName.length == 0) {
        stationButton.setAttribute("class", "blank");

    // connect events to other stationButtons
    } else {
        (function(thisStationName) {
            stationButton.onclick = function() {
                stationName = thisStationName;
                updateLocation();
            }
        })(thisStationName);
    }

}

// select station right/left
/*
function xNav(direction) {
    var activeRow = activeStationButton.parentNode;
    var rowButtons = activeRow.getElementsByTagName("td");
    for (var i = 0; i < rowButtons.length; i++) {
        if (rowButtons[i].innerHTML == stationName) {
            break
        }
    }
    var newButton = rowButtons[i + direction];
    if (typeof newButton !== undefined) {
        newButton.click();
        newButton.focus();
    }
}
*/

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

function xNav(xDirection, yDirection) {
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
    console.log(e.key);
    var i = parseInt(e.key);
    if (Number.isInteger(i) && i <= locationStatuses.length) {
        locationStatus = locationStatuses[i];
        updateLocation();
    } else switch(e.key) {
        case "Enter":
            submitButton.click();
            break;
        case "i":
            locationInput.select();
            break;
        case "h":
        case "ArrowLeft":
            xNav(-1, 0);
            break;
        case "j":
        case "ArrowDown":
            xNav(0, 1);
            break;
        case "k":
        case "ArrowUp":
            xNav(0, -1);
            break;
        case "l":
        case "ArrowRight":
            xNav(1, 0);
            break;
        default:
            break;
    }
}

updateLocation();
