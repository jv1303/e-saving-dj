// Configuração do mapa interativo
function initMapa(pontos) {
    // Inicializar mapa
    const map = L.map('map').setView([-15.7801, -47.9292], 12); // Brasília
    
    // Adicionar tile layer do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    // Adicionar marcadores dos pontos
    pontos.forEach(ponto => {
        if (ponto.latitude && ponto.longitude) {
            const marker = L.marker([ponto.latitude, ponto.longitude])
                .addTo(map)
                .bindPopup(`
                    <b>${ponto.username}</b><br>
                    ${ponto.endereco}<br>
                    Tel: ${ponto.telefone}<br>
                    <small>${ponto.tipos_residuos.join(', ')}</small>
                `);
        }
    });
    
    // Configurar busca
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value;
        if (query) {
            buscarEndereco(query, map);
        }
    });
}

function buscarEndereco(query, map) {
    // Usar Nominatim API do OpenStreetMap para geocodificação
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);
                map.setView([lat, lon], 15);
                
                L.marker([lat, lon])
                    .addTo(map)
                    .bindPopup(`<b>Local procurado:</b><br>${data[0].display_name}`)
                    .openPopup();
            } else {
                alert('Endereço não encontrado');
            }
        })
        .catch(error => {
            console.error('Erro na busca:', error);
            alert('Erro ao buscar endereço');
        });
}