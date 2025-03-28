// static/map.js
// Initialize map and display ocean drift prediction and animated current overlay with error handling

function initMap(origLat = -34.2, origLon = 18.4, driftLat = null, driftLon = null) {
    try {
        // Create the Leaflet map centered on original coordinates
        const map = L.map('map').setView([origLat, origLon], 7);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Leaflet | © OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(map);

        // Mark last known location
        const originMarker = L.marker([origLat, origLon]).addTo(map).bindPopup('Last Known Location');
        originMarker.openPopup();

        // Mark predicted drift location and draw drift path
        if (driftLat !== null && driftLon !== null) {
            L.marker([driftLat, driftLon]).addTo(map).bindPopup('Predicted Location');
            L.polyline([[origLat, origLon], [driftLat, driftLon]], {
                color: 'orange',
                weight: 3
            }).addTo(map);
        }

        // Load animated ocean current vectors
        fetch('/static/current_vectors.json')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch ocean vector data');
                return response.json();
            })
            .then(data => {
                if (!data || !data.data || data.data.length === 0) {
                    console.warn('Vector data is empty or malformed.');
                    return;
                }

                const velocityLayer = L.velocityLayer({
                    displayValues: true,
                    displayOptions: {
                        velocityType: 'Ocean Current',
                        position: 'bottomleft',
                        emptyString: 'No current data',
                        angleConvention: 'bearingCW',
                        speedUnit: 'm/s'
                    },
                    data: data,
                    maxVelocity: 3
                });
                map.addLayer(velocityLayer);
            })
            .catch(err => {
                console.error('[ERROR] Loading current_vectors.json:', err);
            });

    } catch (err) {
        console.error('[ERROR] Initializing map:', err);
    }
}
