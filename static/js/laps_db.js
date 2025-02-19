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

const saveLaps = document.getElementById('save-laps');
saveLaps.addEventListener('click', function(e){
    save_data(e);
}, false);

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

const compareLaps = document.getElementById('compare-laps');
compareLaps.addEventListener('click', function(e){
    get_data(e);
}, false);

function get_data(e){
    e.preventDefault();
    const objectStore = db.transaction('laps').objectStore('laps');
    objectStore.openCursor().onsuccess = (event) => {
        const cursor = event.target.result;
        if (!cursor){
            //console.log('No entries to display.');
            return;
        }
        console.log(cursor.value);
        cursor.continue();
    };
};

const clearLaps = document.getElementById('clear-laps');
clearLaps.addEventListener('click', function(e){
    clear_data(e);
}, false);

function clear_data(e){
    e.preventDefault();
    const transaction = db.transaction(['laps'], 'readwrite');
    transaction.objectStore('laps').clear();

    transaction.oncomplete = () => {
        console.log('Data cleared.');
    };
};