class SeoulBikeMapCard extends HTMLElement {

  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;

    const root = this.shadowRoot;
    if (!root) {
      this.attachShadow({ mode: "open" });
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div id="map" style="height: 500px;"></div>
        </ha-card>
      `;
      this._initMap();
    }

    this._updateMarkers();
  }

  _initMap() {
    this.map = L.map(this.shadowRoot.getElementById("map")).setView([37.48, 127.15], 14);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19
    }).addTo(this.map);

    this.markers = [];
  }

  _updateMarkers() {

    const entityId = this.config.entity;
    const stateObj = this._hass.states[entityId];

    if (!stateObj) return;

    const stations = stateObj.attributes.stations || [];

    this.markers.forEach(m => m.remove());
    this.markers = [];

    stations.forEach(s => {

      if (!s.lat || !s.lon) return;

      let color = "green";

      if (s.bikes === 0) color = "red";
      else if (s.bikes <= 3) color = "orange";

      const marker = L.circleMarker([s.lat, s.lon], {
        radius: 8,
        color: color,
        fillOpacity: 0.8
      }).addTo(this.map);

      marker.bindPopup(`
        <b>${s.name}</b><br>
        🚲 ${s.bikes} / ${s.racks}<br>
        📏 ${s.distance_km.toFixed(2)} km
      `);

      this.markers.push(marker);
    });
  }

  getCardSize() {
    return 6;
  }
}

customElements.define("seoulbike-map-card", SeoulBikeMapCard);