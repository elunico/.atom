/*global L District initialStateZoom Precinct turf currentState geojson stateToAbbr */

/* exports Map style highlightFeature
 * onEachPrecinctFeature */


class Map {
  constructor(tagID, latlng, zoom, zoomStep = 1) {
    this.tagID = tagID;
    this.latlng = latlng;
    this.zoom = zoom;
    this.stateRenderedGeoJson = {}; // stateRenderedGeoJson;
    this.renderedGeoJson = {};
    this.sidebar = undefined;

    this.currentState = undefined;

    this.states = {};
    this.districts = [];
    // todo: delete this
    this.precincts = [];


    this.map =
      L.map(tagID, {
        zoomSnap: 0,
        zoomDelta: zoomStep
      }).setView(latlng, zoom);

    this.map.on('zoomend', (event) => {
      console.log(this.zoom);
      console.log(event.target._zoom);
      if (event.target._zoom > this.zoom) {
        // this.renderPrecincts(1);
      }
    });
  }

  /**
   * Get the request url for a state and its abbreviation
   * @param {State} state initialized with abbreviation
   * @param {number} zoomLevel zoom level for precincts or -1 for initial zoom level
   * @returns {string} request URL
   */
  static urlForState(state, zoomLevel) {
    zoomLevel = (zoomLevel > 0 ? zoomLevel : initialStateZoom[state.abbr]) || 7;
    return '/CSE308/index?state=' + state.abbr + '&zoom=' + zoomLevel;
  }

  getZoom() {
    return this.map.getZoom();
  }

  getOptions() {
    return this.map.options;
  }

  removeLayer(layer) {
    this.map.removeLayer(layer);
  }

  rawMap() {
    return this.map;
  }

  addSidebar(sidebar) {
    this.sidebar = sidebar;
  }

  addTileLayer(url, options) {
    L.tileLayer(url, options).addTo(this.map);
  }

  on(eventName, callback) {
    this.map.on(eventName, callback);
  }

  resetMap(e) {
    e.preventDefault();
    this.unbindStatePopup();
    this.currentState.selected = false;
    this.currentState = undefined;
    // for (let key of Object.keys(this.stateRenderedGeoJson)) {
    //   this.map.removeLayer(this.stateRenderedGeoJson[key]);
    // }
    for (let precinct of this.precincts) {
      precinct.unrender();
    }
    for (let district of this.districts) {
      district.unrender();
    }
    // this.precincts = [];
    // this.districts = [];
    if (this.sidebar) {
      this.sidebar.disableSideButtons();
      this.sidebar.hide();
    }
    this.unlockMap();
    this.setView([38.007, -95.844], 5);
  }

  setView(latlgn, zoom) {
    this.map.setView(latlgn, zoom);
  }

  lockMap() {
    this.map.setMinZoom(Math.floor(this.map.getZoom()));
  }

  unlockMap() {
    this.map.options.minZoom = 0;
  }

  fitBounds(bounds) {
    this.map.fitBounds(bounds);
    this.map.setZoom(Math.floor(this.map.getZoom()));
  }

  renderGeoJson(objectName, gjObject, options) {
    let g = L.geoJson(gjObject, options);
    g.addTo(this.map);
    this.renderedGeoJson[objectName] = g;
    return g;
  }



  dimState() {
    // TODO: This
  }

  stateClicked(event) {
    let stateName = event.target.feature.properties.NAME;
    let abbr = stateToAbbr[stateName];
    console.log(this.currentState);
    console.log(abbr);


    if (this.currentState && this.currentState.abbr !== abbr) {
      this.bindStatePopups();
    } else if (this.currentState) {
      this.unbindStatePopup();
    } else {
      this.unbindStatePopup();

      console.log(event.target);
      this.currentState = this.states[abbr];
      this.currentState.selected = true;

      if (!this.currentState.dataLoaded) {
        let that = this;

        let req = new XMLHttpRequest();
        let reqUrl = Map.urlForState(this.currentState, -1);
        console.log('Fetching ' + this.currentState);
        console.log(reqUrl);
        req.open('GET', reqUrl, true);
        req.onreadystatechange = function ( /*event*/ ) {
          if (req.status === 200 && req.readyState === 4) {
            let b = JSON.parse(req.response);

            console.log(b);
            let districts = b.districts.features;
            let precincts = b.precincts.features;

            // Must do districts first so precincts are visible
            that.addDistrictsFromResponse(districts, that);
            that.addPrecinctsFromResponse(precincts, that);
            that.renderPrecincts(50000000);
            that.calculatePrecinctDistricts(districts, precincts);

            that.currentState.dataLoaded = true;

            that.dimState();
          }
        };
        req.setRequestHeader('Content-Type', 'text/plain');
        req.send();
      } else {
        this.renderDistricts();
        this.renderPrecincts(50000000);
        this.dimState();
      }

      this.fitBounds(event.target.getBounds());
      this.sidebar.enableSideButtons(event);
      this.lockMap();
    }
  }

  calculatePrecinctDistricts(ds, ps) {

    for (let p of ps) {
      for (let d of ds) {
        let box = new L.Polygon(d.geometry);
        let precinctCenter = new L.Polygon(p.layer).getCenter();
        if (box.getBounds().contains(precinctCenter)) {
          d.precincts.push(p);
        }
      }
    }

  }

  addPrecinctsFromResponse(precincts, mapInstance) {
    let idx = 0;
    for (let feature of precincts) {
      let id = feature.properties.countyid + 'p' + idx;
      // let precinctPolygon = turf.polygon(feature.geometry.coordinates[0]);
      let area = feature.properties.shape_area; // turf.area(precinctPolygon);
      let p = new Precinct(id, undefined, feature, undefined, area);
      mapInstance.precincts.push(p);
    }
  }

  renderPrecincts(areaThreshold) {
    for (let i = this.precincts.length - 1; i >= 0; i--) {
      let precinct = this.precincts[i];
      if (precinct.area > areaThreshold) {
        precinct.render(this);
      }
    }
  }

  bindStatePopups() {
    for (let state of Object.values(this.states)) {
      if (!state.selected) {
        state.layer.bindPopup('Reset the map before choosing another state<br/> You will lose current unsaved changes.');
        state.layer.closePopup();
      }
    }
  }

  unbindStatePopup() {
    for (let state of Object.values(this.states)) {
      if (!state.selected) {
        state.layer.closePopup();
        state.layer.unbindPopup();
      }
    }
  }

  /**
   *
   * @param {District[]} districts
   * @param {Map} mapInstance
   */
  addDistrictsFromResponse(districts, mapInstance) {
    for (let feature of districts) {
      // let precinctPolygon = turf.polygon(feature.geometry.coordinates[0]);
      // TODO : undefined stateAbbr
      let p = new District(feature.properties.DISTRICT, feature.properties.stateAbbr, feature);
      mapInstance.districts.push(p);
    }
    this.renderDistricts();
  }

  renderDistricts() {
    for (let d of this.districts) {
      d.render(this);
    }
  }
}
