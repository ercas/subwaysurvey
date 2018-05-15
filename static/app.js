var stationButtons = document.getElementById("subway-lines").getElementsByTagName("td"),
    sourceInput = document.getElementById("source"),
    locationInput = document.getElementById("location"),
    submitButton = document.getElementById("submit"),
    responseFrame = document.getElementById("response-frame");
    stationName = "northeastern";

var statusSelector = document.getElementById("status-selector"),
    valueInput = document.getElementById("value"),
    locationStatuses = ["stopped", "entering", "leaving", "left"],
    locationStatus = 0;

// update the forms and ui to reflect inputs
function updateLocation() {
    locationInput.value = stationName;
    valueInput.value = locationStatus;

    statusButtons = statusSelector.getElementsByTagName("td");
    for (var j = 0; j < statusButtons.length; j++) {
        var statusButton = statusButtons[j];
        if (j == locationStatus) {
            statusButton.setAttribute("class", "selected-status");
        } else {
            statusButton.removeAttribute("class");
        }
    }

    for (var i = 0; i < stationButtons.length; i++) {
        var stationButton = stationButtons[i];
        if (stationButton.innerHTML == stationName) {
            console.log(stationName);
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
    td.innerHTML = thisLocationStatus + " (" + i + ")";
    (function(thisLocationStatus, index) {
        td.onclick = function() {
            locationStatus = index;
            updateLocation();
        }
    })(thisLocationStatus, i);
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

// keybindings
document.onkeydown = function(e) {
    console.log(e.key);
    var i = parseInt(e.key);
    if (Number.isInteger(i) && i <= locationStatuses.length) {
        locationStatus = i;
        updateLocation();
    } else if (e.key == "Enter") {
        submitButton.click();
    }
}

submitButton.onclick = function() {
    responseFrame.setAttribute("src", "about:blank");
}

updateLocation();
