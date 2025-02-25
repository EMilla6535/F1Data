/**
 * Declare and open a database to save laps
 */
let db;
const DBOpenRequest = indexedDB.open('laps', 1);

DBOpenRequest.onerror = (event) => {
    console.log('Error onpening database.');
};

DBOpenRequest.onsuccess = (event) => {
    //console.log('Database initialised.');
    db = DBOpenRequest.result;
    // Maybe clear database every time the page is loaded or the GP is changed
}
DBOpenRequest.onupgradeneeded = (event) => {
    db = event.target.result;
    db.onerror = (event) => {
        console.log('Error loading database in onupgradeneeded.');
    };

    const objectStore = db.createObjectStore('laps', { keyPath: 'driver' });
    objectStore.createIndex('lap_time', 'lap_time', { unique: false });
    objectStore.createIndex('lap_index', 'lap_index', { unique: false });

    //console.log('Object store created.');
}

/**
 * Open a web socket to send data to fastapi for plotting
 */
let ws = new WebSocket("ws://localhost:8000/laps/ws");
ws.onmessage = function(event){
    // Get the plot area
    var plotArea = document.getElementById('plot-area');
    // Remove all child nodes
    while (plotArea.firstChild){
        plotArea.removeChild(plotArea.firstChild);
    }
    // Create img element
    var imgElement = document.createElement('img');
    imgElement.setAttribute('src', 'data:image/png;base64,' + event.data);
    // Append img to plot area
    plotArea.appendChild(imgElement);
};


/**
 * Function to save laps 
 */
function save_data(e){
    // Prevent submit
    e.preventDefault();
    // Open a read/write transaction
    const transaction = db.transaction(['laps'], 'readwrite');

    transaction.oncomplete = () => {
        //console.log('Transaction completed.');
    }
    transaction.onerror = () => {
        console.error('Transaction error on save_data.');
    }

    const driver_name = document.getElementById('driver');
    const lap_times = document.getElementsByName('lap_times');
    const lap_index = document.getElementsByName('lap_index');

    if (lap_times.length > 0){
        let times_array = [];
        let index_array = [];
        
        for (let i = 0; i < lap_times.length; i++) {
            times_array.push(lap_times[i].value);
            index_array.push(lap_index[i].value);
        }
        
        data = {driver: driver_name.value, lap_time: times_array, lap_index: index_array}
        
        const objectStore = transaction.objectStore('laps');
        const objectStoreRequest = objectStore.add(data);
        objectStoreRequest.onsuccess = (event) => {
            //console.log('Request successful.');
        };
    }
};

/**
 * Send data to fastapi for plotting
 */

function get_data(e){
    e.preventDefault();
    // Get folder name
    const folderSelect = document.getElementsByName('folder');
    const objectStore = db.transaction('laps').objectStore('laps');
    // Save data in a persistent array
    let lapData = [];
    objectStore.openCursor().onsuccess = (event) => {
        const cursor = event.target.result;
        if (!cursor){
            //console.log('No entries to display.');
            // If there are no items in the array don't send anything
            // else send the data to python
            if (lapData.length != 0){
                // Make data a JSON structure
                json_data = {folder: folderSelect[0].value, data: lapData};
                console.log(json_data)
                ws.send(JSON.stringify(json_data));
            }
            return;
        }
        //console.log(cursor.value);
        // Save cursor values in array
        lapData.push({
            driver: cursor.value.driver, 
            lap_index: cursor.value.lap_index});
        cursor.continue();
    };
};

/**
 * Clear database
 */

function clear_data(e){
    e.preventDefault();
    const transaction = db.transaction(['laps'], 'readwrite');
    transaction.objectStore('laps').clear();

    transaction.oncomplete = () => {
        console.log('Data cleared.');
    };
};

/**
 * Variables for submit buttons
 */
let saveLaps;
let compareLaps;
let clearLaps;

/**
 * If there is a change in GP, remove lap-select items
 * and clear database to prevent comparison of
 * different GP.
 */
const folderSelect = document.getElementsByName('folder');
folderSelect[0].addEventListener('change', function(){
    const lapSelectDiv = document.getElementById('lap-select');
    // Remove all child nodes
    while (lapSelectDiv.firstChild){
        lapSelectDiv.removeChild(lapSelectDiv.firstChild);
    }
    // Call clear database
    const transaction = db.transaction(['laps'], 'readwrite');
    transaction.objectStore('laps').clear();

    transaction.oncomplete = () => {
        console.log('Database cleared.');
    };
}, false);
