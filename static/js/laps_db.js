saveLaps = document.getElementById('save-laps');
saveLaps.addEventListener('click', function(e){
    save_data(e);
}, false);    

compareLaps = document.getElementById('compare-laps');
compareLaps.addEventListener('click', function(e){
    get_data(e);
}, false);    

clearLaps = document.getElementById('clear-laps');
clearLaps.addEventListener('click', function(e){
    clear_data(e);
}, false);
