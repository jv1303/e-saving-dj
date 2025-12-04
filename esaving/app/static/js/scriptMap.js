document.addEventListener('DOMContentLoaded', function() {
    // 1. Inicializa o Mapa
    var map = L.map('map').setView([-23.5505, -46.6333], 12);

    // 2. Adiciona o visual (Tiles)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // 3. Tenta ler os dados enviados pelo Django
    var dataElement = document.getElementById('pontos-data');
    
    if (dataElement) {
        try {
            var pontos = JSON.parse(dataElement.textContent);

            // 4. Se tiver pontos no banco, desenha eles
            if (pontos && pontos.length > 0) {
                var group = new L.featureGroup();

                pontos.forEach(function(ponto) {
                    // Configura um ícone verde
                    var iconeVerde = new L.Icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    });

                    // Conteúdo do balão ao clicar
                    var conteudoPopup = `
                        <div style="text-align:center;">
                            <h6 style="color:#198754; font-weight:bold; margin-bottom:5px;">${ponto.name}</h6>
                            <small style="color:#666;">${ponto.parceiro}</small><br>
                            <p style="margin: 5px 0;">${ponto.desc}</p>
                            <a href="https://www.google.com/maps/search/?api=1&query=${ponto.lat},${ponto.lon}" 
                               target="_blank" class="btn btn-sm btn-outline-success">Ver no Google Maps</a>
                        </div>
                    `;

                    var marker = L.marker([ponto.lat, ponto.lon], {icon: iconeVerde})
                        .addTo(map)
                        .bindPopup(conteudoPopup);
                    
                    group.addLayer(marker);
                });

                // Ajusta o zoom para mostrar todos os pontos encontrados
                map.fitBounds(group.getBounds().pad(0.1));
            }
        } catch (e) {
            console.error("Erro ao ler dados do mapa:", e);
        }
    }
});