document.addEventListener('DOMContentLoaded', function() {
  // --- Draggable table logic ---
  (function() {
    var dragHandle = document.querySelector('.hotel-table thead');
    var container = document.getElementById('table-container');
    var offsetX = 0, offsetY = 0, isDown = false;
    dragHandle.style.cursor = 'grab';
    dragHandle.addEventListener('mousedown', function(e) {
      isDown = true;
      offsetX = e.clientX - container.offsetLeft;
      offsetY = e.clientY - container.offsetTop;
      container.style.transition = 'none';
      dragHandle.style.cursor = 'grabbing';
    });
    document.addEventListener('mousemove', function(e) {
      if (!isDown) return;
      container.style.left = (e.clientX - offsetX) + 'px';
      container.style.top = (e.clientY - offsetY) + 'px';
    });
    document.addEventListener('mouseup', function(e) {
      if (isDown) {
        isDown = false;
        dragHandle.style.cursor = 'grab';
        container.style.transition = '';
      }
    });
  })();
  // --- Resizable table height logic ---
  (function() {
    var resizeHandle = document.getElementById('table-resize-handle');
    var container = document.getElementById('table-container');
    var startY = 0, startHeight = 0, resizing = false;
    resizeHandle.addEventListener('mousedown', function(e) {
      resizing = true;
      startY = e.clientY;
      startHeight = parseInt(document.defaultView.getComputedStyle(container).height, 10);
      document.body.style.cursor = 'ns-resize';
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!resizing) return;
      var newHeight = Math.max(60, startHeight + (e.clientY - startY));
      container.style.height = newHeight + 'px';
    });
    document.addEventListener('mouseup', function(e) {
      if (resizing) {
        resizing = false;
        document.body.style.cursor = '';
      }
    });
  })();
  // --- Marker/table sync logic ---
  function collectMarkersFromMap() {
    if (!window.map) {
      console.log('collectMarkersFromMap: window.map not ready');
      setTimeout(collectMarkersFromMap, 300);
      return;
    }
    var found = [];
    window.map.eachLayer(function(layer) {
      if (layer instanceof L.CircleMarker) {
        found.push(layer);
      }
    });
    window.markers = found;
    console.log('collectMarkersFromMap: found', found.length, 'markers');
  }
  window.collectMarkers = collectMarkersFromMap;
  // --- Table row click sync ---
  function setupTableRowClicks(markerCount) {
    var rows = document.querySelectorAll('.hotel-table tbody tr');
    console.log('setupTableRowClicks: Found', rows.length, 'rows. markerCount =', markerCount);
    rows.forEach(function(row) {
      row.addEventListener('click', function() {
        var idx = parseInt(row.getAttribute('data-idx'));
        console.log('Row clicked. idx =', idx);
        var marker = window.markers[idx];
        console.log('Marker for idx', idx, '=', marker);
        if (marker && window.map) {
          console.log('Panning to marker and opening popup for idx', idx);
          window.map.setView(marker.getLatLng(), window.map.getZoom(), {animate: true});
          setTimeout(function() { marker.openPopup(); }, 350);
        } else {
          console.log('No marker or map found for idx', idx);
        }
      });
    });
  }
  window.setupTableRowClicks = setupTableRowClicks;
});
