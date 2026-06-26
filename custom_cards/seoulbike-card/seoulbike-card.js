class SeoulBikeCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.map = null;
    }

    setConfig(config) {
        this.config = config;
    }

    set hass(hass) {
        this._hass = hass;
        this.render();
    }

    connectedCallback() {
        this.render();
    }

    render() {
        if (!this.shadowRoot) return;

        this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
      <style>
        #map {
          height: 500px;
          width: 100%;
          border-radius: 12px;
        }
      </style>

      <div id="map"></div>
    `;

        this.initMap();
    }

    initMap() {
        if (this.map) return;

        const L = window.L;

        this.map = L.map(this.shadowRoot.getElementById("map")).setView(
            [37.5665, 126.9780], // 서울 중심
            12
        );

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap"
        }).addTo(this.map);

        this.loadStations();
    }

    loadStations() {
        // 👉 여기서 HA sensor 또는 API 연결
        const stations = this.getMockData();

        stations.forEach((s) => {
            const marker = L.circleMarker([s.lat, s.lng], {
                radius: 6,
                color: this.getColor(s),
                fillOpacity: 0.8
            }).addTo(this.map);

            marker.bindPopup(`
        <b>${s.name}</b><br/>
        대여가능: ${s.available}<br/>
        거치대: ${s.total}
      `);
        });
    }

    getColor(s) {
        const ratio = s.available / s.total;

        if (ratio > 0.5) return "green";
        if (ratio > 0.2) return "orange";
        return "red";
    }

    getMockData() {
        return [
            { name: "강남역 1번출구", lat: 37.498, lng: 127.027, available: 12, total: 20 },
            { name: "역삼역", lat: 37.500, lng: 127.036, available: 3, total: 25 },
            { name: "선릉역", lat: 37.504, lng: 127.048, available: 18, total: 30 }
        ];
    }

    getCardSize() {
        return 6;
    }
}

customElements.define("seoulbike-card", SeoulBikeCard);