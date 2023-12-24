function compareTime(time1, time2) {
    // Compare two time values in the format 'HH:mm'
    const [hours1, minutes1] = time1.split(':').map(Number);
    const [hours2, minutes2] = time2.split(':').map(Number);
    if (hours1 !== hours2) {
        return hours1 - hours2;
    }
    return minutes1 - minutes2;
};
function compareDate(date1, date2) {
    return date1.localeCompare(date2);
}
const setError = (modalId, message) => {
    //console.error(message)
    const inputControl = document.getElementById('inputControl'+modalId);
    if (inputControl) {
        const errorDisplay = inputControl.querySelector('.error');
        errorDisplay.innerText = message;
        inputControl.classList.add('error');
        inputControl.classList.remove('success');
        setTimeout(function () {setSuccess(modalId) ;console.log("Koniec komunikatu o bledzie."); }, 2000);
    }
};
const setSuccess = (modalId) => {
    //console.log("PRZYWROCONO SUKCES")
    const inputControl = document.getElementById('inputControl'+modalId);
    if (inputControl) {
        //console.log("Element = ", inputControl)
        const errorDisplay = inputControl.querySelector('.error');
        if (errorDisplay) { errorDisplay.innerText = ""; }
        inputControl.classList.add('success');
        inputControl.classList.remove('error');
    }
};
function checkIfStartPlusIntervalsEqualEnd(startDateValue, startTimeValue, endDateValue, endTimeValue, interval, breakBetweenIntervals) {
    //console.log("DANE CHECK =", startDateValue, startTimeValue, endDateValue, endTimeValue, interval, breakBetweenIntervals)
    if (typeof interval == undefined || interval == "" || interval === null || interval === 0 || interval === '0') { return true }
    let breakBetweenIntervalsValue = 0;
    if ( breakBetweenIntervals ) {
        breakBetweenIntervalsValue = parseInt(breakBetweenIntervals, 10)
    }
    const intervalTimeValue = parseInt(interval, 10);
    const totalMinutes = (intervalTimeValue + breakBetweenIntervalsValue);
    let validationCondition = false;
    let startDateHelp = new Date(startDateValue + ' ' + startTimeValue)
    let endDateHelp = new Date(endDateValue + ' ' + endTimeValue)
    //console.log(startDateValue, startTimeValue, startDateHelp, totalMinutes)
    while (startDateHelp < endDateHelp) {
        startDateHelp.setMinutes(startDateHelp.getMinutes() + totalMinutes);
        if (startDateHelp.getTime() === endDateHelp.getTime()) {
            //console.log("ROWNA SIE", startDateHelp, endDateHelp)
            validationCondition = true
        }
    }
    return validationCondition
};

function validationModalForm(modalId, e, reservationValidation, submit=true) {
    const startTimeElement = document.getElementById('startTime'+modalId)
    const endTimeElement = document.getElementById('endTime'+modalId)
    const startDateElement = document.getElementById('startDate'+modalId)
    const endDateElement = document.getElementById('endDate'+modalId)
    const intervalTimeElement = document.getElementById('intervalTime'+modalId)
    const breakBetweenIntervalsElement = document.getElementById('breakBetweenIntervals'+modalId)
    const startTimeValue = startTimeElement.value;
    const endTimeValue = endTimeElement.value;
    let startDateValue = null;
    if (startDateElement) { startDateValue = startDateElement.value; }
    let endDateValue = null;
    if (endDateElement) { endDateValue = endDateElement.value; }
    let intervalTimeValue = null;
    if (intervalTimeElement) { intervalTimeValue = intervalTimeElement.value; }
    let breakBetweenIntervalsValue = null;
    if (breakBetweenIntervalsElement) { breakBetweenIntervalsValue = breakBetweenIntervalsElement.value; }

    console.log("DANE VALIDACI: ", startTimeValue, endTimeValue, startDateValue, endDateValue, intervalTimeValue, breakBetweenIntervalsValue, typeof intervalTimeValue, typeof breakBetweenIntervalsValue)
    if (submit) {
        //brak wszystkich wymaganych danych
        if (!startDateValue || !endDateValue || !startTimeValue || !endTimeValue){
            if (e) { e.preventDefault(); }
            setError(modalId, "Wypełnij wszystkie niezbędne pola.")
            return false;
        }
        if (!intervalTimeValue && breakBetweenIntervalsValue !== '0') {
            if (e) { e.preventDefault(); }
            setError(modalId, "Nie można ustawić przerwy bez przedziałów czasowych.")
            return false;
        }
    }
    let availableBookingStartTimeString;
    let availableBookingEndTimeString;
    if (reservationValidation) {
        availableBookingStartTimeString = availableBookingData.startAvailableBookingDate.getHours() + ':' + availableBookingData.startAvailableBookingDate.getMinutes();
        availableBookingEndTimeString = availableBookingData.endAvailableBookingDate.getHours() + ':' + availableBookingData.endAvailableBookingDate.getMinutes();
    }
    if( endDateValue && startDateValue){
        if (compareDate(endDateValue, startDateValue) < 0){
            if (e) { e.preventDefault(); }
            setError(modalId, "Data końcowa nie może być przed datą początku.")
            return false;
        } else if (reservationValidation && (compareDate(startDateValue, availableBookingData.startAvailableBookingDate.toISOString().split('T')[0]) < 0 || compareDate(availableBookingData.endAvailableBookingDate.toISOString().split('T')[0], endDateValue) < 0)){
            if (e) { e.preventDefault(); }
            setError(modalId, "Data wykracza poza date dotępnego terminu.")
            return false;
        } else {
            setSuccess(modalId);
        }
        if (compareDate(endDateValue, startDateValue) === 0 && compareTime(endTimeValue, startTimeValue) <= 0) {
            if (e) { e.preventDefault(); }
            setError(modalId, "Czas końcowy nie może być przed czasem początku.")
            return false;
        } else if (reservationValidation && (compareTime(startTimeValue, availableBookingStartTimeString) < 0 || compareTime(availableBookingEndTimeString, endTimeValue) < 0)){
            if (e) { e.preventDefault(); }
            setError(modalId, "Czas wykracza poza czas dotępnego terminu.")
            return false;
        } else {
            setSuccess(modalId);
        }
        //sprawdzenie czy start + n interwałów z przerwami = koniec
        if (checkIfStartPlusIntervalsEqualEnd(startDateValue, startTimeValue, endDateValue, endTimeValue, intervalTimeValue, breakBetweenIntervalsValue)) {
            setSuccess(modalId);
        } else{
            console.error("Zle przedzialy addCal: ", startDateValue, startTimeValue, endDateValue, endTimeValue, intervalTimeValue, breakBetweenIntervalsValue)
            if (e) { e.preventDefault(); }
            setError(modalId, "Nieprawidłowy podział czasu.");
            return false;
        }
    } else {
        console.error("IF NIE WYWOLAL SIE W WALIDACJI TYLKO CZASY o dziwo potrzebne")
        /*if (compareTime(endTimeValue, startTimeValue) <= 0) {
            if (e) { e.preventDefault(); }
            setError(modalElement, "Czas końcowy nie może być przed czasem początku.")
            return false;
        } else if (compareTime(startTimeValue, availableBookingStartTimeString) < 0 || compareTime(availableBookingEndTimeString, endTimeValue) < 0){
            if (e) { e.preventDefault(); }
            setError(modalElement, "Czas wykracza poza czas dotępnego terminu.")
            return false;
        } else {
            setSuccess(modalElement);
        }*/
    }
    return true;
};

function validateSelectIfThereIsValue(modalId, selectPrefix) {
    const select = document.getElementById(selectPrefix+modalId)
    if (select.value === null || select.value === "" || typeof select.value === 'undefined' ) {
        setError(modalId, 'Musisz wybrać opcje')
        return false;
    }
    setSuccess(modalId)
    return true;
}